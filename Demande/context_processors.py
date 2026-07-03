def notifications_context(request):
    """Injecte le nombre de notifications non lues et les 8 dernières dans tous les templates."""
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {'unread_notifications_count': 0, 'recent_notifications': []}

    from Demande.models import Notification
    # Une seule requête au lieu de deux
    recent = list(
        Notification.objects.filter(destinataire=request.user, lu=False)
        .select_related('demande')
        .order_by('-date_creation')[:8]
    )
    return {
        'unread_notifications_count': len(recent),
        'recent_notifications': recent,
    }
