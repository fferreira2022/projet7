import os
from dotenv import load_dotenv
# load environment variables
load_dotenv()

from api_credit.views import predict, home
import pytest
from django.urls import reverse
from django.test import Client
from django.middleware.csrf import get_token
from django.test.client import RequestFactory

from unittest.mock import patch, MagicMock
import json
import pandas as pd
from api_credit.models import Customer
from bs4 import BeautifulSoup  
import numpy as np

VALID_API_KEY = os.environ.get('VALID_API_KEY')

"""
Rappel des types d'erreurs dans le contexte des tests effectués:

200 OK : La requête a abouti et le serveur a renvoyé la réponse attendue.

400 Bad Request : Si les données envoyées (comme le JSON ou client_id) sont mal formées ou manquantes.

403 Forbidden : la clé API est absente ou invalide dans une requête distante (ou rejet du token pour une requête locale)

404 Not Found : l'ID client envoyé ne correspond à aucun enregistrement dans la base de données.

405 Method Not Allowed : une requête GET est envoyée à la vue predict qui n'accepte que les POST.

500 Internal Server Error : une exception inattendue se produit dans le code (ex: échec de chargement du modèle).

"""

# -------------------------- Premier test ------------------------------------

# Test pour vérifier si une clé API invalide retourne une réponse d'erreur 403
@pytest.mark.django_db
def test_predict_invalid_api_key():
    # client = client (machine) django qui simule une requête HTTP
    client = Client()
    
    headers = {
        'X-API-KEY': 'clé_invalide'  # passer une clé API incorrecte en valeur
    }
    
    # reverse('predict') : Cette fonction génère l'URL de la vue predict à partir de son nom,
    # défini dans le fichier urls.py. Django associe automatiquement cette URL à la fonction predict.
    # la requête POST est envoyée avec la clé api invalide...
    response = client.post(reverse('predict'), content_type='application/json', HTTP_X_API_KEY=headers['X-API-KEY'])
    
    # Vérifie qu'un statut HTTP 403 est retourné
    assert response.status_code == 403
    
    # Vérifie que le message d'erreur est clair, qu'il contient "Clé API invalide ou absente."
    assert "Clé API invalide ou absente." in response.json().get("error", "")


# -------------------------- Second test ------------------------------------

# Test pour vérifier le comportement lorsque des données JSON invalides sont envoyées
# Le décorateur @pytest.mark.django_db indique que ce test aura besoin d'accéder à la base de données Django
# notamment pour récupérer les données du client
@pytest.mark.django_db
def test_predict_invalid_json_format():
    
    # client (machine) django qui simule une requête HTTP
    client = Client()
    
    headers = {
        'X-API-KEY': VALID_API_KEY  # la clé est valide...
    }
    
    invalid_json_data = "Données invalides"  # mais les données ne sont pas au format JSON
    
    # envoyer des données invalides dans la requête vers l'url predict associée à la fonction du même nom...
    response = client.post(
        reverse('predict'),
        data=invalid_json_data,
        content_type='application/json',
        HTTP_X_API_KEY=headers['X-API-KEY']
    )
    
    # Vérifier qu'un statut HTTP 400 est retourné pour des données JSON invalides
    assert response.status_code == 400
    
    # Vérifie la précision du message d'erreur
    assert "Données JSON invalides." in response.json().get("error", "")


# # -------------------------- Troisième test ------------------------------------
 
# test pour vérifier si un dataframe avec un nombre de colonnes incorrect déclenche une erreur
@pytest.mark.django_db
@patch('api_credit.views.validate_api_key')  # Simule l'appel à la fonction validate_api_key
def test_predict_invalid_column_count(mock_validate_api_key):
    client = Client()
    
    # Simule une clé API valide puisque la fonction
    mock_validate_api_key.return_value = None  

    headers = {
        'X-API-KEY': 'clé_valide'  # Clé API valide
    }
    
    # Envoyer des données avec un nombre de colonnes incorrect
    invalid_data = {
        "SK_ID_CURR": 100001,
        "EXT_SOURCE_1": 0.2  # Seulement 2 colonnes au lieu des 26 attendues
    }
    
    response = client.post(
        reverse('predict'),
        data=json.dumps(invalid_data),
        content_type='application/json',
        HTTP_X_API_KEY=headers['X-API-KEY']
    )
    
    # Vérifie qu'une erreur est renvoyée
    assert response.status_code == 400
    
    # Vérifie le message d'erreur
    assert "Le nombre de variables est incorrect." in response.json().get("error", "")




# # -------------------------- Quatrième test ------------------------------------

# vérifier la présence du csrf token dans la requête locale
@pytest.mark.django_db
def test_predict_with_csrf_token():
    client = Client()
    
    # simuler une requête pour obtenir un token CSRF
    response = client.get(reverse('predict'))  # une requête GET 
    csrf_token = get_token(response.wsgi_request) # pour générer un token

    # Simuler les cookies envoyés avec la requête
    client.cookies['csrftoken'] = csrf_token  # nom du cookie CSRF dans Django

    # envoyer une requête POST locale avec le cookie CSRF
    response = client.post(
        reverse('predict'),
        data={"client_id": 100001},  # passer l'id client
        content_type='application/x-www-form-urlencoded',
        HTTP_COOKIE=f'csrftoken={csrf_token}',  # ajouter le cookie CSRF dans les en-têtes
    )
    
    # pour vérifier si la requête passe le filtre CSRF
    # on s'assure que la fonction ne renvoie un code erreur avec le csrftoken passé dans les headers
    # autrement dit, qu'il n'y a pas de rejet CSRF
    assert response.status_code != 403 
    
    # Vérifier si le message d'erreur attendu est conforme en cas d'absence d'id client
    assert "Veuillez sélectionner un ID client." in response.content.decode()  

    
# --------------------------------------- Cinquième test ---------------------------------------------------------

# tester le chargement du modèle de prédiction pour les requêtes distantes
@pytest.mark.django_db
@patch('api_credit.views.get_model')  # Simule la fonction get_model
def test_model_loading_remote(mock_get_model):
    client = Client()
    
    headers = {
        'X-API-KEY': VALID_API_KEY  # Clé API valide
    }
    
    # Simuler que le modèle est introuvable
    mock_get_model.return_value = None

    # définir les données pour un client
    data={
        "SK_ID_CURR": 100091,
        "EXT_SOURCE_1": 0.56,
        "EXT_SOURCE_2": 0.78,
        "EXT_SOURCE_3": 0.65,
        "DAYS_BIRTH": 12000,
        "DAYS_EMPLOYED": 4000,
        "CODE_GENDER_M": True,
        "CREDIT_INCOME_PERCENT": 0.25,
        "ANNUITY_INCOME_PERCENT": 0.12,
        "CREDIT_TERM": 36.5,
        "AMT_CREDIT": 250000.0,
        "AMT_ANNUITY": 15000.0,
        "AMT_INCOME_TOTAL": 100000.0,
        "DAYS_EMPLOYED_PERCENT": 0.33,
        "NAME_INCOME_TYPE_Businessman": False,
        "NAME_INCOME_TYPE_Commercial_associate": True,
        "NAME_INCOME_TYPE_Pensioner": False,
        "NAME_INCOME_TYPE_State_servant": False,
        "NAME_INCOME_TYPE_Student": False,
        "NAME_INCOME_TYPE_Unemployed": False,
        "NAME_INCOME_TYPE_Working": True,
        "NAME_EDUCATION_TYPE_Academic_degree": False,
        "NAME_EDUCATION_TYPE_Higher_education": True,
        "NAME_EDUCATION_TYPE_Incomplete_higher": False,
        "NAME_EDUCATION_TYPE_Lower_secondary": False,
        "NAME_EDUCATION_TYPE_Secondary_secondary_special": False
        }
    
    # effectuer une requête POST
    response = client.post(
        reverse('predict'),
        data=json.dumps(data),
        content_type='application/json',
        HTTP_X_API_KEY=headers['X-API-KEY']
    )

    # Vérifier le statut de la réponse, doit afficher un code 500 si problème de chargement du modèle
    assert response.status_code == 500
    
    # assertion selon laquelle le message d'erreur indique bien que le modèle est introuvable
    assert response.json().get("error") == "Le modèle est introuvable."
    



# -------------------------------------- Sixième test -------------------------------------------------

@pytest.fixture
def mock_model():
    # Création d'un faux modèle
    model = MagicMock()
    model.predict.return_value = np.array([1])  # Simulation d'une prédiction de classe 1
    model.predict_proba.return_value = np.array([[0.2, 0.8]])  # Simulation de probabilités
    return model


# tester si la prédiction est correcte (soit 0 soit 1)
# et si la probabilité est bien comprise entre 0 et 1
@patch('api_credit.views.get_model')
def test_prediction(mock_get_model, mock_model):
    
    mock_get_model.return_value = mock_model
    
    client = Client()
    
    headers = {
        'X-API-KEY': VALID_API_KEY  # Clé API valide
    }


    # définir les données pour un client
    data={
        "SK_ID_CURR": 100091,
        "EXT_SOURCE_1": 0.56,
        "EXT_SOURCE_2": 0.78,
        "EXT_SOURCE_3": 0.65,
        "DAYS_BIRTH": 12000,
        "DAYS_EMPLOYED": 4000,
        "CODE_GENDER_M": True,
        "CREDIT_INCOME_PERCENT": 0.25,
        "ANNUITY_INCOME_PERCENT": 0.12,
        "CREDIT_TERM": 36.5,
        "AMT_CREDIT": 250000.0,
        "AMT_ANNUITY": 15000.0,
        "AMT_INCOME_TOTAL": 100000.0,
        "DAYS_EMPLOYED_PERCENT": 0.33,
        "NAME_INCOME_TYPE_Businessman": False,
        "NAME_INCOME_TYPE_Commercial_associate": True,
        "NAME_INCOME_TYPE_Pensioner": False,
        "NAME_INCOME_TYPE_State_servant": False,
        "NAME_INCOME_TYPE_Student": False,
        "NAME_INCOME_TYPE_Unemployed": False,
        "NAME_INCOME_TYPE_Working": True,
        "NAME_EDUCATION_TYPE_Academic_degree": False,
        "NAME_EDUCATION_TYPE_Higher_education": True,
        "NAME_EDUCATION_TYPE_Incomplete_higher": False,
        "NAME_EDUCATION_TYPE_Lower_secondary": False,
        "NAME_EDUCATION_TYPE_Secondary_secondary_special": False
        }
    
    # effectuer une requête POST
    response = client.post(
        reverse('predict'),
        data=json.dumps(data),
        content_type='application/json',
        HTTP_X_API_KEY=headers['X-API-KEY']
    )

    # charger les données de réponse en JSON
    data = response.json()

    # Vérifiez la prédiction (doit être 0 ou 1)
    assert data['predictions'][0] in [0, 1], "La prédiction doit être 0 ou 1."

    # vérifiez que la probabilité est un nombre décimal compris entre 0 et 1
    assert 0 <= data['probability'] <= 1, "La probabilité doit être entre 0 et 1."
    
    # vérifier que le message d'erreur pour une probabilité incorrecte est suffisamment clair
    if response.status_code == 400:
        assert "La probabilité doit être comprise en 0 et 1" in data.get("error", "")