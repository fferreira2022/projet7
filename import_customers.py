import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')  # Remplacez par le nom de votre projet
django.setup()

import csv
from api_credit.models import Customer  # Remplacez "myapp" par le nom de votre application

# Chemin vers le fichier CSV
csv_file_path = "static/csv/clients_no_log.csv"

# Lire et insérer uniquement les 10 premières lignes
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for i, row in enumerate(reader):
        if i >= 10:  # Arrêter après 10 lignes
            break
        Customer.objects.create(
            SK_ID_CURR=int(row['SK_ID_CURR']),
            EXT_SOURCE_1=float(row['EXT_SOURCE_1']),
            EXT_SOURCE_2=float(row['EXT_SOURCE_2']),
            EXT_SOURCE_3=float(row['EXT_SOURCE_3']),
            DAYS_BIRTH=int(row['DAYS_BIRTH']),
            DAYS_EMPLOYED=float(row['DAYS_EMPLOYED']),
            CODE_GENDER_M=bool(row['CODE_GENDER_M']),
            CREDIT_INCOME_PERCENT=float(row['CREDIT_INCOME_PERCENT']),
            ANNUITY_INCOME_PERCENT=float(row['ANNUITY_INCOME_PERCENT']),
            CREDIT_TERM=float(row['CREDIT_TERM']),
            AMT_CREDIT=float(row['AMT_CREDIT']),
            AMT_ANNUITY=float(row['AMT_ANNUITY']),
            AMT_INCOME_TOTAL=float(row['AMT_INCOME_TOTAL']),
            DAYS_EMPLOYED_PERCENT=float(row['DAYS_EMPLOYED_PERCENT'])
        )