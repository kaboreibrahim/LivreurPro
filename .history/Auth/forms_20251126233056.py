import random
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import *
from django.forms import  DateTimeInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

###### formulaire de connexion

class LoginForm(AuthenticationForm):
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur ou e-mail', 'id':'username' }))
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe', 'id':'password' }))
    

#formulaire de  verificacion

class VerificationForm(forms.Form):
    code = forms.CharField(max_length=6)
    

#formulaire de creation de compte

class CustomForm(UserCreationForm): 
    
    class Meta:
        model = CustomUser
        fields=('first_name', 'last_name', 'photos','email','Contact', 'username','password1', 'password2')
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse e-mail est déjà utilisée")
        return email
    
    def save (self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        
        if commit:
            user.save()
            code=str(random.randint(100000,999999))
            VerificationCode.objects.create(user=user,code=code)
            send_mail(
                'Vérification de votre compte a mon livro pro', 
                f' votre code de verification pour acceder a votre session : {code}',
                'kaboremessi@gmail.com',
                [user.email],
                fail_silently=False,
                )
            
        return user
    