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