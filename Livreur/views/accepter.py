from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from Demande.models import DCL


@login_required
@require_POST
def accepter_course(request, pk):
    """Le livreur accepte la course qui lui a été assignée."""
    demande = get_object_or_404(DCL, id=pk, coursier=request.user)

    if demande.statut != 'VALIDATION_LIVREUR':
        messages.error(request, "Cette action n'est pas disponible pour cette demande.")
        return redirect('Livreur:detail_demande_livreur', pk=pk)

    demande.statut = 'LIVREUR_ROUTE'
    demande.save()

    messages.success(
        request,
        f"Vous avez accepté la course {demande.ref}. "
        "Rendez-vous au point de départ pour récupérer le colis."
    )
    return redirect('Livreur:detail_demande_livreur', pk=pk)
