def notifications_context(request):
    """Injecte le nombre de notifications non lues et les 8 dernières dans tous les templates."""
    if not request.user.is_authenticated:
        return {'unread_notifications_count': 0, 'recent_notifications': []}

    from Demande.models import Notification
    recent = list(
        Notification.objects.filter(destinataire=request.user, lu=False)
        .select_related('demande')
        .order_by('-date_creation')[:8]
    )
    count = Notification.objects.filter(destinataire=request.user, lu=False).count()
    return {
        'unread_notifications_count': count,
        'recent_notifications': recent,
    }
