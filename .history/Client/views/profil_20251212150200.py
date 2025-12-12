from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Sum, Count, Q
from django.contrib.auth import update_session_auth_hash
from Auth.models import CustomUser
from Demande.models import DCL
from Client.forms import (
    ProfileForm, 
    PasswordChangeForm
)


@login_required
def profile(request):
    """
    Vue du profil client avec toutes ses statistiques et informations
    """
    user = request.user
    
    # Récupérer toutes les demandes du client
    demandes = DCL.objects.filter(
        client=user
    ).select_related('coursier').order_by('-date_demande')
    
    # Statistiques des demandes
    total_commandes = demandes.count()
    
    # Demandes en cours (tous les statuts sauf TERMINEE et ANNULEE)
    commandes_en_cours = demandes.filter(
        ~Q(statut='TERMINEE') & ~Q(statut='ANNULEE')
    ).count()
    
    # Demandes livrées
    commandes_livrees = demandes.filter(statut='TERMINEE').count()
    
    # Total dépensé (somme des coûts de livraison des demandes terminées)
    total_depense = demandes.filter(
        statut='TERMINEE',
        cout_livraison__isnull=False
    ).aggregate(
        total=Sum('cout_livraison')
    )['total'] or 0
    
    # Dernières 5 demandes
    dernieres_commandes = demandes[:5]
    
    # Historique complet des livraisons (demandes terminées)
    historique_livraisons = demandes.filter(
        statut='TERMINEE'
    ).order_by('-date_demande')
    
    # Simuler le panier (à adapter selon votre logique de panier)
    # Si vous avez un modèle Panier, adaptez ici
    # Exemple : panier_count = Panier.objects.filter(client=user, est_actif=True).count()
    panier_count = 0
    
    context = {
        'user': user,
        'client': user,
        'total_commandes': total_commandes,
        'commandes_en_cours': commandes_en_cours,
        'commandes_livrees': commandes_livrees,
        'total_depense': total_depense,
        'dernieres_commandes': dernieres_commandes,
        'historique_livraisons': historique_livraisons,
        'panier_count': panier_count,
    }
    
    return render(request, 'profile/profile.html', context)




@login_required
def change_password(request):
    """Vue pour changer le mot de passe du client"""
    try:
        user = request.user
    except user.DoesNotExist:
        messages.error(request, "Vous n'avez pas de profil client.")
        return redirect('Client:profile')
    
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Garde l'utilisateur connecté
            messages.success(request, "Votre mot de passe a été changé avec succès!")
            return redirect('Client:profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = PasswordChangeForm(user=request.user)
    
    context = {
        'form': form,
        'user': user,
    }
    
    return render(request, 'profile/change_password.html', context)



from Auth.models import CustomUser
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction

@login_required
def edit_profile(request):
    """Vue pour modifier le profil du client"""
    user = request.user
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, user=request.user)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Update user fields
                    user.first_name = form.cleaned_data.get('first_name', user.first_name)
                    user.last_name = form.cleaned_data.get('last_name', user.last_name)
                    user.email = form.cleaned_data.get('email', user.email)
                    user.save()
                    
                    messages.success(request, "Votre profil a été mis à jour avec succès!")
                    return redirect('Client:profile')
                    
            except Exception as e:
                messages.error(request, f"Une erreur est survenue lors de la mise à jour du profil: {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ProfileForm(user=request.user)
    
    context = {
        'form': form,
        'user': user,
    }
    
    return render(request, 'profile/edit_profile.html', context)



@login_required
def parametres(request):
    """Vue pour les paramètres du client"""
    try:
        user = request.user
    except Client.DoesNotExist:
        messages.error(request, "Vous n'avez pas de profil client.")
        return redirect('Client:profile')
    
    if request.method == 'POST':
        # Mise à jour des préférences de notifications
        # client.notifications_email = request.POST.get('notifications_email') == 'on'
        # client.notifications_sms = request.POST.get('notifications_sms') == 'on'
        user.save()
        
        messages.success(request, "Vos préférences ont été enregistrées!")
        return redirect('Client:settings')
    
    context = {
        'user': user,
    }
    
    return render(request, 'profile/settings.html', context)
