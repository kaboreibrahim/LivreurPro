from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Demande.models import DCL
 
@login_required
def liste_demandes(request):
    """Vue pour lister toutes les demandes du client"""
    demandes = DCL.objects.filter(client=request.user).order_by('-date_demande')
    
    context = {
        'demandes': demandes,
    }
    
    return render(request, 'livraison/liste.html', context)