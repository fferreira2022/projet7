
import requests

session = requests.Session()

# base de l'URL du site + page predict
session.get("http://127.0.0.1:8000/predict/")

# # token CSRF récupéré depuis Inspecter => Application => Stockage => Cookies => csrftoken => token 
# csrf_token = 'bvKU7vuxpwaIf4cuem76iaKH1PNnlI1C'

# Inclure le token dans les headers pour la requête POST
headers = {
    "X-API-KEY": "hkih8+0qk7hk2dl*!gg*rrl89@14hh4!*z",
    "Content-Type": "application/json",
}
data = {
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

response = session.post("http://127.0.0.1:8000/predict/", json=data, headers=headers)

print(response.json())
