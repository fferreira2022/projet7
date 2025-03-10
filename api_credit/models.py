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