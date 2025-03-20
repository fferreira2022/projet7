import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# clé API (statique)
VALID_API_KEY = os.environ.get('VALID_API_KEY')

# Titre de l'application
st.title("Estimer la probabilité de défaut de crédit d'un client")

# Saisie de l'URL de l'API
api_url = st.text_input("Entrez l'URL de l'API", value="https://projet7-production.up.railway.app/predict/")

# Saisie de la clé API
api_key = st.text_input("Entrez la clé API", type="password")  # Champ masqué pour la clé API

# Ajout d'un champ de texte pour les données JSON avec un exemple
st.header("Entrez les données au format JSON")
json_input = st.text_area(
    "Copiez et collez ici les données au format JSON. Un exemple avec les variables attendues est fourni dans le champ.",
    height=300,
    value='''{
        "SK_ID_CURR": 100001,
        "EXT_SOURCE_1": 0.7526144906031748,
        "EXT_SOURCE_2": 0.7896543511176771,
        "EXT_SOURCE_3": 0.1595195404777181,
        "DAYS_BIRTH": 19241,
        "DAYS_EMPLOYED": 2329.0,
        "CODE_GENDER_M": false,
        "CREDIT_INCOME_PERCENT": 4.213333333333333,
        "ANNUITY_INCOME_PERCENT": 0.1523,
        "CREDIT_TERM": 0.0361471518987341,
        "AMT_CREDIT": 568800.0,
        "AMT_ANNUITY": 20560.5,
        "AMT_INCOME_TOTAL": 135000.0,
        "DAYS_EMPLOYED_PERCENT": 0.1210436048022452,
        "NAME_INCOME_TYPE_Businessman": false,
        "NAME_INCOME_TYPE_Commercial_associate": false,
        "NAME_INCOME_TYPE_Pensioner": false,
        "NAME_INCOME_TYPE_State_servant": false,
        "NAME_INCOME_TYPE_Student": false,
        "NAME_INCOME_TYPE_Unemployed": false,
        "NAME_INCOME_TYPE_Working": true,
        "NAME_EDUCATION_TYPE_Academic_degree": false,
        "NAME_EDUCATION_TYPE_Higher_education": true,
        "NAME_EDUCATION_TYPE_Incomplete_higher": false,
        "NAME_EDUCATION_TYPE_Lower_secondary": false,
        "NAME_EDUCATION_TYPE_Secondary_secondary_special": false
    }'''
)

# Fonction pour valider que l'URL renvoie une réponse JSON conforme
def validate_api_url(api_url, headers):
    try:
        # Requête de test avec un JSON minimal valide
        test_data = {
            "SK_ID_CURR": 100028,
            "EXT_SOURCE_1": 0.5257339776824489,
            "EXT_SOURCE_2": 0.5096770801723647,
            "EXT_SOURCE_3": 0.6127042441012546,
            "DAYS_BIRTH": 13976,
            "DAYS_EMPLOYED": 1866.0,
            "CODE_GENDER_M": False,
            "CREDIT_INCOME_PERCENT": 5.0,
            "ANNUITY_INCOME_PERCENT": 0.1556142857142857,
            "CREDIT_TERM": 0.0311228571428571,
            "AMT_CREDIT": 1575000.0,
            "AMT_ANNUITY": 49018.5,
            "AMT_INCOME_TOTAL": 315000.0,
            "DAYS_EMPLOYED_PERCENT": 0.1335145964510589,
            "NAME_INCOME_TYPE_Businessman": False,
            "NAME_INCOME_TYPE_Commercial_associate": False,
            "NAME_INCOME_TYPE_Pensioner": False,
            "NAME_INCOME_TYPE_State_servant": False,
            "NAME_INCOME_TYPE_Student": False,
            "NAME_INCOME_TYPE_Unemployed": False,
            "NAME_INCOME_TYPE_Working": True,
            "NAME_EDUCATION_TYPE_Academic_degree": False,
            "NAME_EDUCATION_TYPE_Higher_education": False,
            "NAME_EDUCATION_TYPE_Incomplete_higher": False,
            "NAME_EDUCATION_TYPE_Lower_secondary": False,
            "NAME_EDUCATION_TYPE_Secondary_secondary_special": True
        }
        response = requests.post(api_url, headers=headers, json=test_data)

        # Vérifier si la réponse est un JSON et contient les clés attendues
        if response.status_code == 200:
            result = response.json()
            expected_keys = {"source", "SK_ID_CURR", "probability", "predictions", "status", "status_class", "threshold"}
            if not expected_keys.issubset(result.keys()):
                return False  # Format incorrect
            return True
        else:
            return False  # Erreur HTTP

    except Exception as e:
        return False  # Erreur de connexion ou autre

# Bouton pour soumettre la requête
if st.button("Prédire"):
    # Vérification que l'URL et la clé API sont fournies
    if not api_key or api_key != VALID_API_KEY:
        st.error("Veuillez entrer une clé API valide.")
        st.stop()
    if not api_url:
        st.error("Veuillez entrer une URL valide pour votre API.")
        st.stop()

    # Préparer les headers avec la clé API
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key  # La clé API saisie par l'utilisateur est ajoutée
    }

    # validation de l'URL
    if not validate_api_url(api_url, headers):
        st.error("L'URL de l'API ne semble pas renvoyer une réponse JSON au format attendu.")
        st.stop()

    try:
        # vérification et conversion du JSON
        try:
            data = json.loads(json_input)  # Charger les données saisies en JSON
        except json.JSONDecodeError as e:
            st.error(f"Erreur de format JSON : {e}")
            st.stop()

        # envoi de la requête POST avec l'URL saisie, la clé API et les données JSON
        response = requests.post(api_url, headers=headers, json=data)

        # Gestion de la réponse
        if response.status_code == 200:
            result = response.json()
            status = result.get("status", "Non spécifié")
            probability = result.get("probability", "Non spécifiée")
            threshold = result.get("threshold", "Non spécifié")  # Récupérer le threshold

            # affichage basé sur le statut
            if status == "Accepté":
                st.success("Crédit accepté !")
            elif status == "Refusé":
                st.error("Crédit refusé !")  # Message rouge pour refus

            # couleur de la probabilité en fonction du seuil
            if probability > threshold:
                st.error(f"Probabilité de défaut (supérieure ou égale au seuil) : {probability}")
            else:
                st.success(f"Probabilité de défaut : {probability}")
            
            # afficher le seuil de défaut dans un champ supplémentaire (si probabilité >= seuil => défaut) 
            st.write(f"Seuil de défaut : {threshold}")

        else:
            st.error(f"Erreur {response.status_code} : {response.json().get('error', 'Erreur lors de l\'envoi ou réception de la requête')}")

    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")

