import os
from dotenv import load_dotenv
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
from .models import CustomUser, Customer
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

from django.views.decorators.csrf import csrf_exempt, csrf_protect
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

import mlflow.pyfunc
import mlflow # Utilisé pour charger des modèles MLflow
from mlflow.sklearn import load_model
from mlflow.tracking import MlflowClient

import json
import pandas as pd

import joblib
from joblib import load
import pickle
from django.shortcuts import get_object_or_404
import numpy as np

import lime.lime_tabular
import matplotlib
matplotlib.use('Agg')  # Utilise le backend sans interface graphique
import matplotlib.pyplot as plt

from django.templatetags.static import static

from lime.lime_tabular import LimeTabularExplainer


# load environment variables
load_dotenv()

'''
--------------- Views django | Fichier Backend de l'application --------------

Note: une view django = fonction python

'''


# view de la page d'accueil 
def home(request):
    return render(request, 'api_credit/home.html')


# view de la page depuis laquelle l'utilisateur choisi un client
# et un modèle qui va effectuer une prédiction 
def api(request):
    # afficher certaines données client 
    customers = Customer.objects.values(
        'SK_ID_CURR',
        'DAYS_BIRTH',
        'CODE_GENDER_M',
        'DAYS_EMPLOYED',
        'AMT_CREDIT',
        'AMT_INCOME_TOTAL'
    )
    #  # Ajoutez un débogage pour vérifier les valeurs
    # import pprint
    # pprint.pprint(list(customers))  # Affiche les données dans la console
    # Renvoyer le contexte
    return render(request, 'api_credit/api.html', context={'all_customers': customers})



# -------------------------- Fonction principale | Fonction testée dans test_functions.py  --------------------------

# fonction qui effectue la prédiction pour un client choisi par l'utilisateur test_functions.py  --------------------------

# clé API (statique)
VALID_API_KEY = os.environ.get('VALID_API_KEY')

def validate_api_key(request):
    """
    Fonction pour valider la clé API à partir des en-têtes de la requête.
    """
    api_key = request.headers.get('X-API-KEY')  # récupérer la clé API dans les headers
    if not api_key or api_key != VALID_API_KEY:
        return JsonResponse({"error": "Clé API invalide ou absente."}, status=403)

    return None  # retourne None si la clé est valide ou une erreur sinon


# # récupérer le modèle directement depuis mlflow ui
# def get_model(name, version):
#     """
#     Fonction pour charger un modèle MLflow scikit-learn par son nom et sa version.
#     """
#     try:
#         model = load_model(f"models:/{name}/{version}")
#         return model
#     except Exception as e:
#         raise ValueError(f"Erreur lors du chargement du modèle {name} version {version} : {str(e)}")

# # récupérer le modèle
def get_model():
    """
    Fonction pour charger un modèle scikit-learn depuis un fichier local avec un chemin prédéfini.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_path, "../mlartifacts/166092811025692203/6a092d75528f46c0bf4fbf1cb5f93daf/artifacts/mlflow_model/model.pkl")

    try:
        # Charger le modèle à partir du fichier spécifié
        
        model = joblib.load(filepath)
        return model
    except Exception as e:
        raise ValueError(f"Erreur lors du chargement du modèle à partir de {filepath} : {str(e)}")


# fonction pour récupérer le seuil optimisé du modèle
def get_threshold():
    """
    Fonction pour récupérer le seuil (meilleur threshold) sauvegardé localement.
    """
    filepath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../mlruns/166092811025692203/6a092d75528f46c0bf4fbf1cb5f93daf/metrics/best_threshold"
    )
    try:
        # Lire le contenu du fichier
        with open(filepath, 'r') as file:
            data = file.read().strip()  # Supprimer les espaces ou sauts de ligne

        # Extraire la seconde valeur (le seuil) en divisant par les espaces
        threshold_value = data.split()[1]  # Récupère le deuxième élément (index 1)

        # Convertir en float et arrondir
        threshold = round(float(threshold_value), 3)
        return threshold
    except FileNotFoundError:
        raise ValueError(f"Fichier introuvable au chemin : {filepath}")
    except ValueError as e:
        raise ValueError(f"Erreur lors de la récupération du seuil : {str(e)}")
    except Exception as e:
        raise ValueError(f"Une erreur imprévue est survenue : {str(e)}")


# fonction predict (fonction principale de l'appllication)
@csrf_exempt
def predict(request):
    if request.method == 'POST':
        # on vérifie si la requête est distante 
        is_remote = not request.headers.get('Cookie')  # Pas de cookie dans les headers = requête distante
        
        if not is_remote:  # Si c'est une requête locale
            # appliquer dynamiquement la protection CSRF aux requêtes locales
            # de façon à contourner l'ajout du décorateur @csrf_exempt pour les requêtes distantes
            csrf_protect(lambda req: None)(request)

        if is_remote:
            # si la requête est distante il faut fournir une clé API valide pour aller plus loin
            key_error_response = validate_api_key(request)
            if key_error_response:
                return key_error_response  # on retourne une erreur si la clé est absente ou invalide

        try:
            if is_remote:
                # gestion des requêtes distantes
                # si la valeur de Content-Type est différente de application/json...
                if request.content_type != 'application/json':
                    return JsonResponse({"error": "Le format de la requête doit être JSON."}, status=400)

                try:
                    request_data = json.loads(request.body)  # charger les données json
                except json.JSONDecodeError:
                    return JsonResponse({"error": "Données JSON invalides."}, status=400)

                input_data = pd.DataFrame([request_data])  # convertir en DataFrame
                if input_data.shape[1] != 26:  # vérifier si le nombre de colonnes est correct
                    return JsonResponse({"error": "Le nombre de variables est incorrect."}, status=400)

            else:
                # gestion des requêtes locales (utilisateurs inscrits)
                client_id = request.POST.get('client_id')
                if not client_id:
                    return render(request, 'api_credit/predict.html', 
                                {"error_message": "Veuillez sélectionner un ID client."})

                # chargement des données client
                customers = Customer.objects.all()
                client_data = customers.filter(SK_ID_CURR=client_id).values()
                if not client_data:
                    return render(request, 'api_credit/predict.html', 
                                {"error_message": f"Aucune donnée trouvée pour l'ID client {client_id}."})

                input_data = pd.DataFrame(client_data)  # Convertir en DataFrame

            # transformation log et suppression des colonnes inutiles
            if 'AMT_INCOME_TOTAL' in input_data.columns:
                input_data['AMT_INCOME_TOTAL_log'] = input_data['AMT_INCOME_TOTAL'].apply(lambda x: np.log1p(x) if x > 0 else 0)
            if 'DAYS_EMPLOYED' in input_data.columns:
                input_data['DAYS_EMPLOYED_log'] = input_data['DAYS_EMPLOYED'].apply(lambda x: np.log1p(abs(x)) if x < 0 else 0)
            if 'CREDIT_INCOME_PERCENT' in input_data.columns:
                input_data['CREDIT_INCOME_PERCENT_log'] = input_data['CREDIT_INCOME_PERCENT'].apply(lambda x: np.log1p(x) if x > 0 else 0)
            if 'AMT_ANNUITY' in input_data.columns:
                input_data['AMT_ANNUITY_log'] = input_data['AMT_ANNUITY'].apply(lambda x: np.log1p(x) if x > 0 else 0)

            columns_to_remove = ['AMT_INCOME_TOTAL', 'DAYS_EMPLOYED', 'CREDIT_INCOME_PERCENT', 'AMT_ANNUITY']
            input_data.drop(columns=[col for col in columns_to_remove if col in input_data.columns], inplace=True)

            #------------------ Processus commun aux requêtes distantes et locales (via l'application) -------------------
            
            # charger le modèle imposé (en l'occurrence LogisticRegression)
            # model = get_model("LogisticRegression", 10)
            model = get_model()
            
            if model is None and is_remote:
                return JsonResponse({"error": "Le modèle est introuvable."}, status=500)
            if model is None and not is_remote:
                return render(request, 'api_credit/predict.html', 
                                {"error_message": "Erreur lors du chargement du modèle."})
                

            # # récupérer le seuil logué dans MLflow
            # client = MlflowClient()
            # run_id = "6a092d75528f46c0bf4fbf1cb5f93daf"  
            # metrics = client.get_run(run_id).data.metrics
            # threshold = metrics.get("best_threshold", None)  # Récupération du seuil (par défaut None s'il est absent)
            
            # récupérer le seuil sauvegardé en local
            try:
                threshold = get_threshold()
                print(f"Seuil récupéré : {threshold}")
            except ValueError as e:
                return JsonResponse({"error": f"Impossible de récupérer le seuil : {str(e)}"}, status=500)

            # Réaliser les prédictions
            X_features = input_data.drop(columns=['SK_ID_CURR'], errors='ignore')
            predictions = model.predict(X_features)
            # probability = float(model.predict_proba(X_features)[:, 1])
            probability = round(float(model.predict_proba(X_features)[:, 1]), 3)
            
            if predictions not in [0, 1]:
                if is_remote:
                    return JsonResponse({"error": "La prédiction doit être 0 ou 1"}, status=400)
                if not is_remote:
                    return render(request, 'api_credit/predict.html', 
                                {"error_message": "La prédiction doit être 0 ou 1"})
                    
            if not 0 <= probability <= 1:
                if is_remote:
                    return JsonResponse({"error": "La probabilité doit être comprise en 0 et 1"}, status=400)
                if not is_remote:
                    return render(request, 'api_credit/predict.html', 
                                {"error_message": "La probabilité doit être comprise en 0 et 1"})
                


            status = "Accepté" if predictions == 0 else "Refusé"
            status_class = "text-success" if predictions == 0 else "text-danger"

            # stocker les résultats dans le dictionnaire context
            context = {
                "source": "Requête distante" if is_remote else "Utilisateur inscrit",
                "SK_ID_CURR": "" if is_remote else client_id,
                "probability": probability,
                "predictions": predictions.tolist(),
                "status": status,
                "status_class": status_class,
                "threshold": threshold 
            }
            
            #------------------ fin du processus commun -----------------

            if not is_remote:
                # Charger l'explainer LIME depuis MLflow
                # lime_artifact_path = mlflow.artifacts.download_artifacts("mlflow-artifacts:/166092811025692203/6a092d75528f46c0bf4fbf1cb5f93daf/artifacts/explainers/lime_explainer_params.joblib")
                
                # charger le lime explainer sauvegardé en local
                lime_explainer_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "../mlartifacts/166092811025692203/6a092d75528f46c0bf4fbf1cb5f93daf/explainers/lime_explainer_params.joblib"
                )
                try:
                    params = joblib.load(lime_explainer_path)
                    explainer = LimeTabularExplainer(
                        training_data=params['training_data'],
                        feature_names=params['feature_names'],
                        mode=params['mode']
                    )
                except FileNotFoundError:
                    raise ValueError(f"Fichier introuvable au chemin : {lime_explainer_path}")
                except Exception as e:
                    raise ValueError(f"Erreur lors du chargement du Lime Explainer : {str(e)}")

                # Récupérer les données du client correspondant à l'id client
                selected_client_data = input_data[input_data['SK_ID_CURR'] == int(client_id)]

                # Vérifier si des données existent pour cet ID
                if selected_client_data.empty:
                    return render(
                        request,
                        'api_credit/predict.html',
                        {"error_message": f"Aucune donnée trouvée pour l'ID client {client_id}."}
                    )

                # Préparer les données du client pour LIME
                X_features_array = selected_client_data.drop(columns=['SK_ID_CURR'], errors='ignore').to_numpy()

                # Générer l'explication LIME pour ce client
                lime_exp = explainer.explain_instance(
                    X_features_array[0],  # Données du client sous forme de tableau
                    model.predict_proba,
                    num_features=10  # Nombre de caractéristiques à expliquer
                )

                # Créer un graphique LIME
                static_images_path = os.path.join(settings.BASE_DIR, 'static', 'images')  # Répertoire cible
                os.makedirs(static_images_path, exist_ok=True)  # Créez le dossier s'il n'existe pas
                lime_graph_path = os.path.join(static_images_path, f'lime_graph_{client_id}.png')  # Nom unique basé sur l'ID client
                lime_exp.as_pyplot_figure()
                plt.title(f"Variables qui ont le plus contribué à la prédiction pour le client {client_id}")
                plt.savefig(lime_graph_path, bbox_inches = 'tight')
                plt.close()

                # Ajouter le chemin statique au contexte
                context["lime_graph"] = f'images/lime_graph_{client_id}.png'

            # envoi des résultats au format json si requête distante, au format html sinon
            if is_remote:
                return JsonResponse(context, status=200)  # Réponse en JSON pour les requêtes distantes
            else:
                return render(request, 'api_credit/predict.html', context)

        except Exception as e:
            if is_remote:
                return JsonResponse({"error": f"Une erreur est survenue : {str(e)}"}, status=500)
            else:
                return render(request, 'api_credit/predict.html', 
                                {"error_message": f"Une erreur est survenue : {str(e)}"})

    return JsonResponse({"error": "Seules les requêtes POST sont acceptées."}, status=405)



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
    # structure du mail envoyé à l'utilisateur
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
            # si le formulaire est correctement rempli l'utilisateur est 
            # sauvegardé en BDD avec un statut inactif tant qu'il n'a pas cliqué sur le lien 
            # d'activation qui lui a été envoyé à l'adresse mail indiquée
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

# view pour la déconnexion de l'utilisateur
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

# suppression du compte de l'utilisateur
@login_required(login_url='login')
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Votre compte a été supprimé.")
        return redirect('home') 
    else:
        return render(request, 'api_credit/delete_account.html')
