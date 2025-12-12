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