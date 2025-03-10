from flask import Flask, request, jsonify
import mlflow.pyfunc

# Charger le modèle depuis le registre MLflow
model = mlflow.pyfunc.load_model("models:/nom_du_modele/production")

# Créer l'application Flask
app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    # Obtenir les données envoyées à l'API (format JSON)
    data = request.get_json()
    
    # Convertir les données en DataFrame (si nécessaire)
    import pandas as pd
    input_data = pd.DataFrame(data)
    
    # Faire une prédiction
    prediction = model.predict(input_data)
    
    # Retourner le résultat
    return jsonify({"prediction": prediction.tolist()})

if __name__ == "__main__":
    app.run(debug=True)
    
    
    
# commande bash pour tester l'api:
# curl -X POST -H "Content-Type: application/json" -d '[{"feature1": 1, "feature2": 2}]' http://127.0.0.1:5000/predict

# Commande YAML pour déployer l'API sur Railway:
# name: Deploy to Railway

# on:
#   push:
#     branches:
#       - main

# jobs:
#   deploy:
#     runs-on: ubuntu-latest
#     steps:
#       - name: Checkout code
#         uses: actions/checkout@v3

#       - name: Setup Python
#         uses: actions/setup-python@v4
#         with:
#           python-version: 3.9

#       - name: Install dependencies
#         run: |
#           pip install -r requirements.txt

#       - name: Deploy to Railway
#         run: |
#           railway up --service-name votre-projet
#         env:
#           RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

