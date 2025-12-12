from django import forms
from Demande.models import DCL

class DCLForm(forms.ModelForm):
    class Meta:
        model = DCL
        fields = [
            'adresse_depart',
            'latitude_depart',
            'longitude_depart',
            'adresse_destination',
            'latitude_destination',
            'longitude_destination',
            'Contact_destinateur',
            'description_colis',
            'poids_colis',
            'valeur_colis',
            'date_recuperation',
            'type_course',
            'instructions',
            'photo_colis1',
            'photo_colis2',
        ]
        
        widgets = {
            'adresse_depart': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'adresse-depart',
                'placeholder': 'Rechercher l\'adresse de départ',
                'readonly': 'readonly',
            }),
            'latitude_depart': forms.HiddenInput(attrs={'id': 'latitude-depart'}),
            'longitude_depart': forms.HiddenInput(attrs={'id': 'longitude-depart'}),
            
            'adresse_destination': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'adresse-destination',
                'placeholder': 'Rechercher l\'adresse de destination',
                'readonly': 'readonly',
            }),
            'latitude_destination': forms.HiddenInput(attrs={'id': 'latitude-destination'}),
            'longitude_destination': forms.HiddenInput(attrs={'id': 'longitude-destination'}),
            
            'Contact_destinateur': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: +225 07 XX XX XX XX',
            }),
            
            'description_colis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez le contenu du colis...',
            }),
            
            'poids_colis': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Poids en kg',
                'step': '0.01',
                'min': '0.01',
            }),
            
            'valeur_colis': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Valeur en FCFA',
                'step': '0.01',
                'min': '0',
            }),
            
            'date_recuperation': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            
            'type_course': forms.Select(attrs={
                'class': 'form-control',
            }),
            
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Instructions supplémentaires (optionnel)...',
            }),
           'photo_colis1' : forms.ClearableFileInput(attrs={'id': 'photo_colis1', 'placeholder': 'Téléchargez l\'image du colis 1'}),
            'photo_colis2' :forms.ClearableFileInput(attrs={'id': 'photo_colis2', 'placeholder': 'Téléchargez l\'image du colis 2'})
        
        }





"""
profile client
"""

class ClientProfileForm(forms.ModelForm):
    # Champs utilisateur
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
    
    class Meta:
        model = Client
        fields = ['telephone', 'notifications_email', 'notifications_sms']
        
        labels = {
            'telephone': 'Téléphone',
            'notifications_email': 'Notifications par email',
            'notifications_sms': 'Notifications par SMS',
        }
        
        widgets = {
            'telephone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': '+225 XX XX XX XX XX'
            }),
            'notifications_email': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-primary bg-gray-100 border-gray-300 rounded focus:ring-primary focus:ring-2'
            }),
            'notifications_sms': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-primary bg-gray-100 border-gray-300 rounded focus:ring-primary focus:ring-2'
            }),
        }
    
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
        from django.contrib.auth.models import User
        # Vérifier l'unicité en excluant l'utilisateur actuel
        if User.objects.exclude(pk=self.user.pk).filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email


class ClientPasswordChangeForm(PasswordChangeForm):
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