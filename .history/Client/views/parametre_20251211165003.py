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