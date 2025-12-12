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
def client_edit_profile(request):
    """Vue pour modifier le profil du client"""
    try:
        client = request.user.client
    except Client.DoesNotExist:
        messages.error(request, "Vous n'avez pas de profil client.")
        return redirect('Accueil')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=client, user=request.user)
        
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
        form = ProfileForm(instance=client, user=request.user)
    
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
        form = PasswordChangeForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Garde l'utilisateur connecté
            messages.success(request, "Votre mot de passe a été changé avec succès!")
            return redirect('client_profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = PasswordChangeForm(user=request.user)
    
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
    
    return render(request, 'profile/settings.html', context)

  