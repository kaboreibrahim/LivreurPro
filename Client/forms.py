from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from Auth.models import CustomUser

# DCLForm est défini dans Demande/forms.py (source unique de vérité)
from Demande.forms import DCLForm  # noqa: F401 — réexporté pour les imports existants





"""
profile 
"""

class ProfileForm(forms.Form):
    first_name = forms.CharField(
        label="Prénom",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Votre prénom'
        })
    )
    last_name = forms.CharField(
        label="Nom",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Votre nom'
        })
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'votre@email.com'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pré-remplir les champs utilisateur
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        from Auth.models import CustomUser
        # Vérifier l'unicité en excluant l'utilisateur actuel
        if CustomUser.objects.exclude(pk=self.user.pk).filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email


class PasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Mot de passe actuel",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Votre mot de passe actuel'
        })
    )
    
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Nouveau mot de passe'
        })
    )
    
    new_password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Confirmer le nouveau mot de passe'
        })
    )