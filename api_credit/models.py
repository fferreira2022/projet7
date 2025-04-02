from django.db import models

from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MaxValueValidator

# Create your models here.

class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',  # Nom unique
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',  # Nom unique
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

class Register_form(models.Model):
    username = models.CharField(max_length=200)
    password1 = models.CharField(max_length=200)
    password2 = models.CharField(max_length=200)
    
class Customer(models.Model):
    SK_ID_CURR = models.IntegerField(primary_key=True)
    EXT_SOURCE_1 = models.FloatField()
    EXT_SOURCE_2 = models.FloatField()
    EXT_SOURCE_3 = models.FloatField()
    DAYS_BIRTH = models.IntegerField()
    DAYS_EMPLOYED = models.FloatField()
    CODE_GENDER_M = models.BooleanField(default=False)
    CREDIT_INCOME_PERCENT = models.FloatField()
    ANNUITY_INCOME_PERCENT = models.FloatField()
    CREDIT_TERM = models.FloatField()
    AMT_CREDIT = models.FloatField()
    AMT_ANNUITY = models.FloatField()
    AMT_INCOME_TOTAL = models.FloatField()
    DAYS_EMPLOYED_PERCENT = models.FloatField()
    NAME_INCOME_TYPE_Businessman = models.BooleanField(default=False)
    NAME_INCOME_TYPE_Commercial_associate = models.BooleanField(default=False)
    NAME_INCOME_TYPE_Pensioner = models.BooleanField(default=False)
    NAME_INCOME_TYPE_State_servant = models.BooleanField(default=False)
    NAME_INCOME_TYPE_Student = models.BooleanField(default=False)
    NAME_INCOME_TYPE_Unemployed = models.BooleanField(default=False)
    NAME_INCOME_TYPE_Working = models.BooleanField(default=False)
    NAME_EDUCATION_TYPE_Academic_degree = models.BooleanField(default=False)
    NAME_EDUCATION_TYPE_Higher_education = models.BooleanField(default=False)
    NAME_EDUCATION_TYPE_Incomplete_higher = models.BooleanField(default=False)
    NAME_EDUCATION_TYPE_Lower_secondary = models.BooleanField(default=False)
    LOAN_TYPE_Cash_0_or_Revolving_1 = models.IntegerField(default=0)
    CNT_CHILDREN = models.IntegerField(default=0)
    REG_REGION_NOT_WORK_REGION = models.IntegerField(default=0)
    OWN_CAR_AGE = models.FloatField(default=0)
    def __str__(self):
        return f"Customer {self.SK_ID_CURR}"

