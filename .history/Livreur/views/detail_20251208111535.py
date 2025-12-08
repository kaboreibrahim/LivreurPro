from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Demande.models import DCL
from django.conf import settings
from Client.decorators import role_required

@login_required
@role_required("livreur")
def detail_demande_livreur(request, pk):
    """Vue pour afficher le détail d'une demande"""
    demande = get_object_or_404(DCL, id=pk, client=request.user)
    
    context = {
        'demande': demande,
        'mapbox_token': settings.MAPBOX_ACCESS_TOKEN,
    }
    
    return render(request, 'livraison/detail_demande.html', context)

 