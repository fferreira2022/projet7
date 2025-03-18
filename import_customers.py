import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')  # Remplacez par le nom de votre projet
django.setup()

import csv
from api_credit.models import Customer  # Remplacez "myapp" par le nom de votre application

# Chemin vers le fichier CSV
csv_file_path = "static/csv/clients_test.csv"

# Lire et insérer uniquement les 15 premières lignes
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for i, row in enumerate(reader):
        if i >= 15:  # Arrêter après 15 lignes
            break
        Customer.objects.create(
            SK_ID_CURR=int(row['SK_ID_CURR']),
            EXT_SOURCE_1=float(row['EXT_SOURCE_1']),
            EXT_SOURCE_2=float(row['EXT_SOURCE_2']),
            EXT_SOURCE_3=float(row['EXT_SOURCE_3']),
            DAYS_BIRTH=int(row['DAYS_BIRTH']),
            DAYS_EMPLOYED=float(row['DAYS_EMPLOYED']),
            CODE_GENDER_M=row['CODE_GENDER_M'].strip() == 'True',
            CREDIT_INCOME_PERCENT=float(row['CREDIT_INCOME_PERCENT']),
            ANNUITY_INCOME_PERCENT=float(row['ANNUITY_INCOME_PERCENT']),
            CREDIT_TERM=float(row['CREDIT_TERM']),
            AMT_CREDIT=float(row['AMT_CREDIT']),
            AMT_ANNUITY=float(row['AMT_ANNUITY']),
            AMT_INCOME_TOTAL=float(row['AMT_INCOME_TOTAL']),
            DAYS_EMPLOYED_PERCENT=float(row['DAYS_EMPLOYED_PERCENT']),
            NAME_INCOME_TYPE_Businessman=row['NAME_INCOME_TYPE_Businessman'].strip() in ['1', 'True', 'true'],
            NAME_INCOME_TYPE_Commercial_associate=row['NAME_INCOME_TYPE_Commercial_associate'].strip() in ['1', 'True', 'true'],
            NAME_INCOME_TYPE_Pensioner=row['NAME_INCOME_TYPE_Pensioner'].strip() in ['1', 'True', 'true'],
            NAME_INCOME_TYPE_State_servant=row['NAME_INCOME_TYPE_State_servant'].strip() in ['1', 'True', 'true'],
            NAME_INCOME_TYPE_Student=row['NAME_INCOME_TYPE_Student'].strip() in ['1', 'True', 'true'],
            NAME_INCOME_TYPE_Unemployed=row['NAME_INCOME_TYPE_Unemployed'].strip() in ['1', 'True', 'true'],
            NAME_INCOME_TYPE_Working=row['NAME_INCOME_TYPE_Working'].strip() in ['1', 'True', 'true'],
            NAME_EDUCATION_TYPE_Academic_degree=row['NAME_EDUCATION_TYPE_Academic_degree'].strip() in ['1', 'True', 'true'],
            NAME_EDUCATION_TYPE_Higher_education=row['NAME_EDUCATION_TYPE_Higher_education'].strip() in ['1', 'True', 'true'],
            NAME_EDUCATION_TYPE_Incomplete_higher=row['NAME_EDUCATION_TYPE_Incomplete_higher'].strip() in ['1', 'True', 'true'],
            NAME_EDUCATION_TYPE_Lower_secondary=row['NAME_EDUCATION_TYPE_Lower_secondary'].strip() in ['1', 'True', 'true'],
            NAME_EDUCATION_TYPE_Secondary_secondary_special=row['NAME_EDUCATION_TYPE_Secondary_secondary_special'].strip() in ['1', 'True', 'true'],
        )
