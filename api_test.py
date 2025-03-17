
import requests

session = requests.Session()

# base de l'URL du site + page predict
session.get("http://127.0.0.1:8000/predict/")

# token CSRF récupéré depuis Inspecter => Application => Stockage => Cookies => csrftoken => token 
csrf_token = 'IyqekZAHd4pmohXKPYIfbcrprBfMiHeZ'

# Inclure le token dans les headers pour la requête POST
headers = {
    "X-CSRFToken": csrf_token,
    "Accept": "application/json",
    "Cookie": "csrftoken="+csrf_token
}
data = {
    "model": "LogisticRegression",
    "client_id": "100091"
}
response = session.post("http://127.0.0.1:8000/predict/", data=data, headers=headers)

print(response.json())

