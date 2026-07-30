from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from Demande.models import DCL


@login_required
@require_POST
def confirmer_recuperation_expediteur(request, pk):
    """Le livreur confirme la récupération du colis avec la signature de l'expéditeur.

    Réservé aux demandes invité (sans compte client) : pour ces demandes, la
    confirmation habituelle du client (Client:confirmer_recuperation) est impossible
    car il n'y a pas de compte pour se connecter.
    """
    demande = get_object_or_404(DCL, id=pk, coursier=request.user)

    if demande.client_id is not None:
        messages.error(
            request,
            "Cette action n'est disponible que pour les demandes sans compte client. "
            "Le client doit confirmer lui-même la récupération du colis."
        )
        return redirect('Livreur:detail_demande_livreur', pk=pk)

    if demande.statut != 'LIVREUR_ROUTE':
        messages.error(request, "Cette action n'est pas disponible pour cette demande.")
        return redirect('Livreur:detail_demande_livreur', pk=pk)

    signature = request.POST.get('signature', '').strip()
    if not signature or not signature.startswith('data:image/png;base64,'):
        messages.error(request, "La signature de l'expéditeur est requise.")
        return redirect('Livreur:detail_demande_livreur', pk=pk)

    demande.signature_expediteur = signature
    demande.statut = 'RECEPTION_COLIS'
    demande.save()

    messages.success(
        request,
        f"Vous avez confirmé la récupération du colis pour la demande {demande.ref}. "
        "Vous êtes maintenant en route vers le destinataire."
    )
    return redirect('Livreur:detail_demande_livreur', pk=pk)


@login_required
@require_POST
def commencer_livraison(request, pk):
    """Le livreur confirme qu'il a récupéré le colis et démarre la livraison."""
    demande = get_object_or_404(DCL, id=pk, coursier=request.user)

    if demande.statut != 'RECEPTION_COLIS':
        messages.error(request, "Cette action n'est pas disponible pour cette demande.")
        return redirect('Livreur:detail_demande_livreur', pk=pk)

    demande.statut = 'LIVRAISON_EN_ROUTE'
    demande.save()

    messages.success(
        request,
        f"Vous avez démarré la livraison de la demande {demande.ref}. "
        "Rendez-vous à l'adresse du destinataire."
    )
    return redirect('Livreur:detail_demande_livreur', pk=pk)


@login_required
@require_POST
def confirmer_livraison(request, pk):
    """Le livreur enregistre la signature du destinataire et termine la livraison."""
    demande = get_object_or_404(DCL, id=pk, coursier=request.user)

    if demande.statut != 'LIVRAISON_EN_ROUTE':
        messages.error(request, "Cette action n'est pas disponible pour cette demande.")
        return redirect('Livreur:detail_demande_livreur', pk=pk)

    signature = request.POST.get('signature', '').strip()
    if not signature or not signature.startswith('data:image/png;base64,'):
        messages.error(request, "La signature du destinataire est requise.")
        return redirect('Livreur:detail_demande_livreur', pk=pk)

    demande.signature_destinataire = signature
    demande.date_livraison = timezone.now()
    demande.statut = 'TERMINEE'
    demande.save()

    messages.success(
        request,
        f"La livraison de la demande {demande.ref} est terminée. Merci !"
    )
    return redirect('Livreur:detail_demande_livreur', pk=pk)
