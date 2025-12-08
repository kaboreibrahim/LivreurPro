from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Demande.models import DCL
from django.conf import settings
from Client.decorators import role_required

@login_required
def detail_demande_livreur(request, pk):
    """Vue pour afficher le détail d'une demande pour un livreur"""
    demande = get_object_or_404(DCL, id=pk)
    
    # Vérifier que le livreur est bien assigné à cette demande
    if demande.coursier != request.user:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Vous n'êtes pas autorisé à voir cette demande.")
    
    context = {
        'demande': demande,
        'mapbox_token': settings.MAPBOX_ACCESS_TOKEN,
    }
    
    return render(request, 'livreur/detail_demande.html', context)