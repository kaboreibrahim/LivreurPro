from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from Client.decorators import role_required
from Demande.models import DCL
# Réutilise le builder PDF du module client
from Client.views.pdf import _build_pdf


@login_required
@role_required("gestionnaire")
def recu_pdf_gestionnaire(request, pk):
    """Génère et retourne le reçu PDF d'une livraison terminée (accès gestionnaire)."""
    demande = get_object_or_404(DCL, id=pk)

    if demande.statut != 'TERMINEE':
        raise Http404("Le reçu n'est disponible qu'après la livraison.")

    buffer = _build_pdf(demande)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="recu-{demande.ref}.pdf"'
    return response
