import os
from typing import Any, Dict
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from .forms import ContactForm, SignUpForm, UpdateProfileForm
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import check_password
from django import forms

from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.core.exceptions import ValidationError

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage

from .tokens import account_activation_token
import uuid 

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.utils import timezone
# import imghdr

from django.core.paginator import Paginator

# import stripe
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse

import mlflow.pyfunc  # Utilisé pour charger des modèles MLflow
import json

'''
-------------------------------------- Views django ---------------------------
'''

def home(request):
    return render(request, 'api_credit/home.html')

def portfolio(request):
    return render(request, 'api_credit/portfolio.html')


# activation du compte après inscription, fait appel au fichier tokens.py
def activate(request, uidb64, token):
    user = request.user
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        
        messages.success(request, f'Votre compte a bien été activé')
        return redirect('login')
    else:
        messages.error(request, "Le lien d'activation n'est pas valide")
    return redirect('home')

# confirmation de l'adresse email
def confirm_Email(request, user, to_email):
    mail_subject = 'Confirm your email address'
    message = render_to_string('api_credit/confirm_email.html', {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user.username}, please confirm your email address by clicking on the following activation link.')
    else:
        messages.error(request, f"An error has occurred during sending of the activation link to {to_email} ")
    # return render(request,'api_credit/confirm_email.html', {'email': email})

# formulaire d'inscription
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.is_active = False
            user.save()  
            
            confirm_Email(request, user, form.cleaned_data.get('email'))
            return redirect('home')
        else:
            messages.error(request, "An error has occurred during registration")
    else:
        form = SignUpForm()
        
    return render(request = request, template_name='api_credit/register.html', context={'form': form})



# formulaire de connexion
def loginPage(request):
    page = 'login'
    # si l'utilisateur est déjà connecté on le redirige vers la page d'accueil
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid email address')
            return redirect('login')
        if user.check_password(password):
            # Si le mot de passe est correct, on connecte l'utilisateur
            login(request, user)
            return redirect('home')
        else:
            # si le mot de passe est incorrect, on affiche un message d'erreur
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    context ={'page': page}
    return render(request, 'api_credit/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')

# profil utilisateur
@login_required(login_url='login') 
def userProfile(request, pk):
    user = CustomUser.objects.get(id=pk)
    email = user.email
    password = user.password
    
    context = {'user': user, 'email': email, 'password' : password}
    return render(request, 'api_credit/profile.html', context)


# modification du profil utilisateur
@login_required(login_url='login') 
def updateProfile(request):
    current_user = CustomUser.objects.get(id=request.user.id)
    form = UpdateProfileForm(instance=current_user)
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=current_user)
        if form.is_valid():
            form.save()
            login(request, current_user)
            messages.success(request, 'Your profile was updated successfully.')
    context = {'form': form, 'user': current_user}
    return render(request, 'api_credit/update_profile.html', context)

        
@login_required(login_url='login')
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('home') 
    else:
        return render(request, 'api_credit/delete_account.html')
    

@login_required(login_url='login')
def scoring_api(request):
    if request.method == 'POST':
        # Charger les données envoyées dans la requête
        try:
            data = json.loads(request.body)
            model_name = data.get("model", "CreditScoringModel")  # Nom du modèle
            features = data.get("features", {})
        except (KeyError, ValueError) as e:
            return JsonResponse({"error": "Requête invalide ou données manquantes"}, status=400)

        # Charger le modèle depuis le Model Registry en production
        try:
            model_uri = f"models:/{model_name}/production"  # Modèle dans le registre MLflow
            model = mlflow.pyfunc.load_model(model_uri)
        except Exception as e:
            return JsonResponse({"error": f"Erreur lors du chargement du modèle : {str(e)}"}, status=500)

        # Effectuer une prédiction avec les features fournies
        try:
            prediction = model.predict([features])
            prob_default = prediction[0]  # Exemple : probabilité de défaut
            category = 1 if prob_default > 0.5 else 0  # Catégorie basée sur un seuil
        except Exception as e:
            return JsonResponse({"error": f"Erreur pendant la prédiction : {str(e)}"}, status=500)

        # Retourner les résultats
        return JsonResponse({
            "probability_of_default": prob_default,
            "category": category
        })

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

