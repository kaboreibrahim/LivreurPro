from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from Demande.models import DCL
from Client.decorators import role_required


@login_required
@role_required("client")
@require_POST
def accepter_prix(request, pk):
    """Le client accepte le prix proposé par le gestionnaire."""
    demande = get_object_or_404(DCL, id=pk, client=request.user)

    if demande.statut != 'VALIDATION_CLIENT':
        messages.error(request, "Cette action n'est pas disponible pour cette demande.")
        return redirect('Client:detail_demande', pk=pk)

    demande.statut = 'VALIDATION_LIVREUR'
    demande.save()

    messages.success(
        request,
        f"Vous avez accepté le prix de {demande.cout_livraison} FCFA "
        f"pour la demande {demande.ref}. Un livreur va être assigné."
    )
    return redirect('Client:detail_demande', pk=pk)
