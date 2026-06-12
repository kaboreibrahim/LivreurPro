from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from Demande.models import DCL
from Client.decorators import role_required


@login_required
@role_required("client")
@require_POST
def confirmer_recuperation(request, pk):
    """Le client confirme que le livreur a récupéré le colis."""
    demande = get_object_or_404(DCL, id=pk, client=request.user)

    if demande.statut != 'LIVREUR_ROUTE':
        messages.error(request, "Cette action n'est pas disponible pour cette demande.")
        return redirect('Client:detail_demande', pk=pk)

    demande.statut = 'RECEPTION_COLIS'
    demande.save()

    messages.success(
        request,
        f"Vous avez confirmé la récupération du colis pour la demande {demande.ref}. "
        "Le livreur est maintenant en route vers le destinataire."
    )
    return redirect('Client:detail_demande', pk=pk)
