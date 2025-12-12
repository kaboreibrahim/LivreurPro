from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from Auth.models import CustomUser
from Demande.models import DCL
from Client.forms import (
    ProfileForm, 
    PasswordChangeForm
)

from django.contrib.auth import update_session_auth_hash


@login_required
def profile(request):
    # """Vue pour afficher le profil du client"""
    # try:
    #     user = request.user
    # except Client.DoesNotExist:
    #     messages.error(request, "Vous n'avez pas de profil client.")
    #     return redirect('home')
    
    # # Statistiques des commandes
    # commandes = Commande.objects.filter(client=client)
    # total_commandes = commandes.count()
    # commandes_en_cours = commandes.filter(
    #     statut__in=['en_attente', 'confirmee', 'en_preparation', 'expedie']
    # ).count()
    # commandes_livrees = commandes.filter(statut='livree').count()
    
    # # # Montant total dépensé
    # # total_depense = commandes.filter(statut='livree').aggregate(
    # #     total=Sum('montant_total')
    # # )['total'] or 0
    
    # # Dernières commandes
    # dernieres_commandes = commandes.order_by('-created_at')[:5]
    
    # # # Articles dans le panier
    # # panier_count = 0
    # # if hasattr(client, 'panier'):
    # #     panier_count = client.panier.lignes.count()
    
    # adresses = client.adresses.all()
    
    # context = {
    #     'client': client,
    #     'total_commandes': total_commandes,
    #     'commandes_en_cours': commandes_en_cours,
    #     'commandes_livrees': commandes_livrees,
    #     # 'total_depense': total_depense,
    #     'dernieres_commandes': dernieres_commandes,
    #     # 'panier_count': panier_count,
    #     'adresses': adresses,
    # }
    
    return render(request, '/profil/profile.html')
 