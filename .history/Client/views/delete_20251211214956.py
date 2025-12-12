from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Demande.models import DCL
from Client.decorators import role_required

@login_required
def annuler_commande(request, ref):
    """
    Vue pour annuler une commande
    """
    if request.method == 'POST':
        user = request.user
        
        # Récupérer la demande
        demande = get_object_or_404(
            DCL,
            ref=ref,
            client=user
        )
        
        # Vérifier si la commande peut être annulée
        statuts_annulables = ['EN_ATTENTE', 'VALIDATION_CLIENT']
        
        if demande.statut in statuts_annulables:
            try:
                demande.statut = 'ANNULEE'
                demande.save()
                messages.success(
                    request, 
                    f'La commande #{demande.ref} a été annulée avec succès.'
                )
            except Exception as e:
                messages.error(
                    request, 
                    f'Une erreur est survenue : {str(e)}'
                )
        else:
            messages.error(
                request, 
                'Cette commande ne peut plus être annulée.'
            )
    
    return redirect('')