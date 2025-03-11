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
import pandas as pd

from joblib import load

'''
-------------------------------------- Views django ---------------------------
'''


def home(request):
    return render(request, 'api_credit/home.html')

def result(request):
    return render(request, 'api_credit/result.html')


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
    mail_subject = 'Confirmer votre adresse email'
    message = render_to_string('api_credit/confirm_email.html', {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Cher(e) {user.username}, veuillez confirmer votre adresse email en cliquant sur le lien suivant.')
    else:
        messages.error(request, f"Une erreur s'est produite pendant l'envoi du lien d'activation à {to_email} ")
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
            messages.error(request, "Une erreur s'est produite lors de l'inscription")
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
            messages.error(request, 'Adresse email invalide')
            return redirect('login')
        if user.check_password(password):
            # Si le mot de passe est correct, on connecte l'utilisateur
            login(request, user)
            return redirect('home')
        else:
            # si le mot de passe est incorrect, on affiche un message d'erreur
            messages.error(request, 'Nom d\'utilisateur ou mot de passe invalide')
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
            messages.success(request, 'Votre profil a été mis à jour.')
    context = {'form': form, 'user': current_user}
    return render(request, 'api_credit/update_profile.html', context)

        
@login_required(login_url='login')
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Votre compte a été supprimé.")
        return redirect('home') 
    else:
        return render(request, 'api_credit/delete_account.html')
    

def predict(request):
    if request.method == 'POST':
        try:
            # Récupérer le modèle sélectionné par l'utilisateur
            selected_model = request.POST.get('model')
            if not selected_model:
                return JsonResponse({"error": "Veuillez sélectionner un modèle."}, status=400)
            
            # Charger le modèle LogisticRegression si sélectionné
            if selected_model == 'LogisticRegression':
                # Définir le chemin absolu vers le modèle
                model_path = os.path.join(settings.BASE_DIR, 'best_models', 'LogisticRegression.joblib')
                # Charger le modèle
                model = load(model_path)
            else:
                return JsonResponse({"error": f"Le modèle '{selected_model}' n'est pas disponible."}, status=400)

            # Initialiser les données
            data = None
            
            # Vérifier les données saisies manuellement
            data_input = request.POST.get('data_input')
            if data_input:
                try:
                    # Convertir les données JSON saisies en DataFrame
                    data_dict = json.loads(data_input)
                    data = pd.DataFrame(data_dict, index=[0]) if isinstance(data_dict, dict) else pd.DataFrame(data_dict)
                except json.JSONDecodeError:
                    return JsonResponse({"error": "Les données saisies ne sont pas au format JSON valide."}, status=400)

            # Vérifier le fichier téléchargé
            file_input = request.FILES.get('file_input')
            if file_input:
                if file_input.name.endswith('.csv'):
                    data = pd.read_csv(file_input)
                elif file_input.name.endswith('.json'):
                    data = pd.read_json(file_input)
                else:
                    return JsonResponse({"error": "Format de fichier non supporté. Veuillez fournir un fichier CSV ou JSON."}, status=400)

            # Vérifier si des données ont été fournies
            if data is None:
                return JsonResponse({"error": "Aucune donnée fournie. Veuillez entrer des données ou télécharger un fichier."}, status=400)

            # Effectuer la prédiction avec le modèle
            # Séparer SK_ID_CURR des features
            
            identifier = int(data['SK_ID_CURR'].values[0])
            X_features = data.drop(columns=['SK_ID_CURR'])
            
            predictions = model.predict(X_features)
            probability = float(model.predict_proba(X_features)[:, 1])
            
            # Préparer et retourner les résultats
            context = {
                "SK_ID_CURR": identifier,
                "model": selected_model,
                "probability": probability,
                "predictions": predictions.tolist(),
            }
            return render(request, 'api_credit/predict.html', context)

        except Exception as e:
            return render(request, 'api_credit/predict.html', {"error_message": f"Une erreur est survenue : {str(e)}"})

    return render(request, 'api_credit/predict.html', {"error_message": "Seules les requêtes POST sont acceptées."})





