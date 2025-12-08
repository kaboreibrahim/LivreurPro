from django.utils import timezone  # Ajout de l'import correct
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from Auth.models import CustomUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
def index_livreur(request, *args, **kwargs):
    if request.user.is_authenticated:
        messages.add_message(
            request, 
            messages.SUCCESS, 
            f"Bienvenue, {request.user.first_name} {request.user.last_name} (Livreur) !"
        )
       
    
    return render(request, 'index_livreur.html', {'page_name': 'Accueil Livreur'})
 
 