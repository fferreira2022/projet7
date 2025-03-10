from django.forms import ModelForm
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django import forms
from django.core.mail import send_mail
from django.core.validators import EmailValidator
from django.conf import settings

            
class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['placeholder'] = 'Email address'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'
        

class UpdateProfileForm(UserChangeForm):
    username = forms.CharField(max_length=200, widget= forms.TextInput(attrs={'class': 'form-control'}), required=False)
    email = forms.EmailField(max_length=200, widget= forms.TextInput(attrs={'class': 'form-control'}), required=False)
    class Meta:
        model = CustomUser
        fields = ['username', 'email']
    
class ContactForm(forms.Form):
    from_email = forms.CharField(validators=[EmailValidator()], widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email'}), required=True)
    subject = forms.CharField(max_length=200, widget= forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}), required=True)
    message = forms.CharField(widget= forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your message'}), required= True)


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address for your admin account'}),
        max_length=254,
        required=True,
    )
    
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New password'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
        strip=False,
    )