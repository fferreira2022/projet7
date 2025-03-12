from api_credit.views import predict, home
import pytest
from django.urls import reverse
from django.test import Client
from unittest.mock import patch
import json
import pandas as pd
from api_credit.models import Customer


# -------------------------- Premier test ------------------------------------

# tester si un modèle a bien été choisi par l'utilisateur 
# (premier bloc de code de la fonction predict dans le fichier views.py)
@pytest.mark.django_db
def test_predict_no_model_selected():
    # client = client (machine) django qui simule une requête HTTP
    client = Client()
    
    # reverse('predict') : Cette fonction génère l'URL de la vue predict à partir de son nom,
    # défini dans le fichier urls.py. Django associe automatiquement cette URL à la fonction predict.
    # la requête POST est envoyée sans données (dictionnaire vide)...
    response = client.post(reverse('predict'), data={})
    
    # ... et on teste si un message d'erreur (code HTTP 400) est bien envoyé à l'utilisateur
    # si l'assertion est fausse (cad si aucun message d'erreur n'est envoyé) le test échouera
    assert response.status_code == 400
    
    # on vérifie si le message d'erreur contient un message clair précisant le type d'erreur
    # en l'occurrence que l'utilisateur n'a sélectionné aucun modèle pour la prédiction
    assert "Veuillez sélectionner un modèle." in response.json().get("error", "")



# -------------------------- Second test ------------------------------------

# tester si le modèle choisi par le client existe / est proposé par l'API
@pytest.mark.django_db
# Le décorateur ci-dessus indique que ce test aura besoin d'accéder à la base de données Django.
# notamment pour récupérer les données du client
def test_predict_invalid_model():
    client = Client()
    # simule un dictionnaire contenant le nom du modèle invalide choisi par l'utilisateur
    data = {
        "model": "InvalidModel", # simule un choix de modèle invalide
        "client_id": "12345" # paire clé valeur non pertinente ici
    }
    
    # reverse('predict') génère l'URL de la vue predict.
    # la méthode client.post(...) envoie une requête POST vers la view predict 
    # avec les données définies dans le dictionnaire data
    response = client.post(reverse('predict'), data=data)
    
    # assertion selon laquelle un message d'erreur / code HTTP 400 (mauvaise requête) 
    # est envoyé à l'utilisateur lorsque le modèle sélectionné est invalide.
    assert response.status_code == 400
    
    # assertion selon laquelle une chaîne de caractères du style "Le modèle 'InvalidModel' n'est pas disponible."
    # est présente dans le message d'erreur envoyé à l'utilisateur
    assert "Le modèle 'InvalidModel' n'est pas disponible." in response.json().get("error", "")



# -------------------------- Troisième test ------------------------------------
 
# tester si l'absence d'identifiant client dans les données transmises par l'utilisateur
# déclenche bel et bien l'envoi d'une erreur à celui-ci
@pytest.mark.django_db
def test_predict_no_client_id():
    client = Client()
    data = {
        # dictionnaire dans lequel l'id client est délibérément omis
        "model": "LogisticRegression" 
    }
    # envoi de la requête à la view predict
    response = client.post(reverse('predict'), data=data)
    
    # assertion selon laquelle un code erreur HTTP 400 est bien envoyé
    # si l'assertion est fausse le test échoue
    assert response.status_code == 400
    
    # assertion selon laquelle une chaîne de caractères du style "Veuillez sélectionner un client."
    # est présente dans le message d'erreur envoyé à l'utilisateur
    assert "Veuillez sélectionner un client." in response.json().get("error", "")



# -------------------------- Quatrième test ------------------------------------

# tester si l'absence d'un id client (en base de données) déclenche une erreur
@pytest.mark.django_db
def test_predict_client_not_found():
    client = Client()  
    data = {
        "model": "LogisticRegression",
        "client_id": "1111199999"  # ID présent mais inexistant en BDD
    }
    # envoi de la requête à la fonction predict
    response = client.post(reverse('predict'), data=data)
    
    # voir explication dans les tests plus haut
    assert response.status_code == 404
    
    # si un message d'erreur approprié est envoyé à l'utilisateur en cas d'id client invalide
    # le test passe sinon il échoue
    assert "Aucune donnée trouvée pour l'ID client" in response.json().get("error", "")


# -------------------------- Cinquième test ------------------------------------

@pytest.mark.django_db
@patch('api_credit.views.load')  # simule le chargement du modèle choisi
@patch('api_credit.views.Customer.objects.all')  # simule la récupération des données clients en BDD

def test_if_data_is_correct(mock_customers, mock_model_load):
    client = Client()  # machine pytest-django pour la simulation
    # simuler les données d'un client
    mock_customers.return_value.filter.return_value.values.return_value = [
        {   # id client inclus pour correspondre au DataFrame attendu par la fonction predict
            "SK_ID_CURR": "12345",  
            "EXT_SOURCE_1": 0.09,
            "EXT_SOURCE_2": 0.91,
            "EXT_SOURCE_3": 0.01,
            "DAYS_BIRTH": 15000,
            "DAYS_EMPLOYED_log": 8.5,
            "CODE_GENDER_M": True,
            "CREDIT_INCOME_PERCENT_log": 0.01,
            "ANNUITY_INCOME_PERCENT": 0.33,
            # "CREDIT_TERM": 0.8,   # simuler que certaines variables sont manquantes
            # "AMT_CREDIT": 451000,
            # "AMT_ANNUITY_log": 0.78,
            # "AMT_INCOME_TOTAL_log": 0.22,
            # "DAYS_EMPLOYED_PERCENT": 0.52
        }
    ]
    # Simulation de la requête POST 
    # à noter que Les autres données nécessaires pour la prédiction (comme EXT_SOURCE_1, DAYS_BIRTH, etc.)
    # ne sont pas envoyées dans la requête. Elles sont récupérées dynamiquement depuis la base de données
    # en fonction de l'ID client fourni.
    response = client.post(reverse('predict'), data={
        "model": "LogisticRegression",
        "client_id": "12345"
    })
    # assertion envoi d'un code erreur...
    assert response.status_code == 400
    # et assertion envoi d'un message approprié
    assert "Le nombre de variables n'est pas celui attendu." in response.json().get("error", "")


# -------------------------------- Sizième test ------------------------------------
