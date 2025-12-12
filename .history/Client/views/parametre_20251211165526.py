from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from Auth.models import Client, Adresse
from Gestionnaire.models import DCL
from account.forms import (
    ClientProfileForm, 
    ClientPasswordChangeForm
)
from account.adresse_forms import AdresseForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta


@login_required
def client_profile(request):
    """Vue pour afficher le profil du client"""
    try:
        client = request.user.client
    except Client.DoesNotExist:
        messages.error(request, "Vous n'avez pas de profil client.")
        return redirect('home')
    
    # Statistiques des commandes
    commandes = Commande.objects.filter(client=client)
    total_commandes = commandes.count()
    commandes_en_cours = commandes.filter(
        statut__in=['en_attente', 'confirmee', 'en_preparation', 'expedie']
    ).count()
    commandes_livrees = commandes.filter(statut='livree').count()
    
    # # Montant total dépensé
    # total_depense = commandes.filter(statut='livree').aggregate(
    #     total=Sum('montant_total')
    # )['total'] or 0
    
    # Dernières commandes
    dernieres_commandes = commandes.order_by('-created_at')[:5]
    
    # # Articles dans le panier
    # panier_count = 0
    # if hasattr(client, 'panier'):
    #     panier_count = client.panier.lignes.count()
    
    adresses = client.adresses.all()
    
    context = {
        'client': client,
        'total_commandes': total_commandes,
        'commandes_en_cours': commandes_en_cours,
        'commandes_livrees': commandes_livrees,
        # 'total_depense': total_depense,
        'dernieres_commandes': dernieres_commandes,
        # 'panier_count': panier_count,
        'adresses': adresses,
    }
    
    return render(request, 'client/profil/profile.html', context)
 

@login_required
def client_edit_profile(request):
    """Vue pour modifier le profil du client"""
    try:
        client = request.user.client
    except Client.DoesNotExist:
        messages.error(request, "Vous n'avez pas de profil client.")
        return redirect('Accueil')
    
    if request.method == 'POST':
        form = ClientProfileForm(request.POST, instance=client, user=request.user)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Sauvegarder les modifications de l'utilisateur
                    user = request.user
                    user.first_name = form.cleaned_data.get('first_name', user.first_name)
                    user.last_name = form.cleaned_data.get('last_name', user.last_name)
                    user.email = form.cleaned_data.get('email', user.email)
                    user.save()
                    
                    # Sauvegarder le profil client
                    form.save()
                    
                    messages.success(request, "Votre profil a été mis à jour avec succès!")
                    return redirect('client_profile')
            except Exception as e:
                messages.error(request, f"Une erreur est survenue: {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ClientProfileForm(instance=client, user=request.user)
    
    context = {
        'form': form,
        'client': client,
    }
    
    return render(request, 'client/profil/edit_profile.html', context)


@login_required
def client_change_password(request):
    """Vue pour changer le mot de passe du client"""
    try:
        client = request.user.client
    except Client.DoesNotExist:
        messages.error(request, "Vous n'avez pas de profil client.")
        return redirect('home')
    
    if request.method == 'POST':
        form = ClientPasswordChangeForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Garde l'utilisateur connecté
            messages.success(request, "Votre mot de passe a été changé avec succès!")
            return redirect('client_profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ClientPasswordChangeForm(user=request.user)
    
    context = {
        'form': form,
        'client': client,
    }
    
    return render(request, 'client/profil/change_password.html', context)


@login_required
def client_settings(request):
    """Vue pour les paramètres du client"""
    try:
        client = request.user.client
    except Client.DoesNotExist:
        messages.error(request, "Vous n'avez pas de profil client.")
        return redirect('home')
    
    if request.method == 'POST':
        # Mise à jour des préférences de notifications
        client.notifications_email = request.POST.get('notifications_email') == 'on'
        client.notifications_sms = request.POST.get('notifications_sms') == 'on'
        client.save()
        
        messages.success(request, "Vos préférences ont été enregistrées!")
        return redirect('client_settings')
    
    context = {
        'client': client,
    }
    
    return render(request, 'client/profil/settings.html', context)

  