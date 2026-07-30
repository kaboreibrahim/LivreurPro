from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse, NoReverseMatch


def _get_gestionnaires():
    from Auth.models import CustomUser
    return list(CustomUser.objects.filter(role='gestionnaire'))


def _build_url(viewname, pk):
    try:
        return reverse(viewname, kwargs={'pk': pk})
    except NoReverseMatch:
        return '#'


def _create_notif(destinataire, demande, titre, message, type_notif, lien=''):
    from .models import Notification
    Notification.objects.create(
        destinataire=destinataire,
        demande=demande,
        titre=titre,
        message=message,
        type_notif=type_notif,
        lien=lien,
    )


def _liberer_livreur(demande):
    """Remet le statut du livreur à LIBRE si un coursier est assigné à la demande."""
    coursier = demande.coursier
    if coursier is None:
        return
    try:
        profil = coursier.livreur
        if profil.is_available != 'LIBRE':
            profil.is_available = 'LIBRE'
            profil.save(update_fields=['is_available'])
    except Exception:
        pass


def create_notifications_for_dcl(demande, old_statut, new_statut):
    """Crée les notifications selon le changement de statut de la demande."""
    client = demande.client
    coursier = demande.coursier
    ref = demande.ref

    client_url = _build_url('Client:detail_demande', demande.pk)
    livreur_url = _build_url('Livreur:detail_demande_livreur', demande.pk)
    gestionnaire_url = _build_url('Gestionnaire:detail_demande', demande.pk)

    if old_statut is None:
        # Nouvelle demande créée
        if client:
            _create_notif(
                client, demande,
                "Demande créée",
                f"Votre demande {ref} a bien été enregistrée et est en cours de traitement.",
                'success', client_url,
            )
        for g in _get_gestionnaires():
            _create_notif(
                g, demande,
                "Nouvelle demande de livraison",
                f"Une nouvelle demande {ref} attend votre validation.",
                'info', gestionnaire_url,
            )

    elif new_statut == 'VALIDATION_CLIENT':
        if client:
            cout = demande.cout_livraison or '–'
            _create_notif(
                client, demande,
                "Prix de livraison proposé",
                f"Le coût de votre livraison {ref} a été fixé à {cout} FCFA. Veuillez valider.",
                'warning', client_url,
            )

    elif new_statut == 'VALIDATION_LIVREUR':
        if coursier:
            # Un livreur a été assigné par le gestionnaire
            if client:
                _create_notif(
                    client, demande,
                    "Livreur assigné",
                    f"Un livreur a été assigné à votre demande {ref}.",
                    'info', client_url,
                )
            _create_notif(
                coursier, demande,
                "Nouvelle course assignée",
                f"La course {ref} vous a été assignée. Veuillez confirmer votre prise en charge.",
                'info', livreur_url,
            )
        else:
            # Pas encore de livreur : soit le client vient d'accepter le prix,
            # soit (demande invité) le gestionnaire a défini le prix directement.
            if client:
                titre = "Prix accepté — assignez un livreur"
                message = f"Le client a accepté le prix de la demande {ref}. Veuillez assigner un livreur."
            else:
                titre = "Prix défini — assignez un livreur"
                message = f"Le prix de la demande invité {ref} a été défini. Veuillez assigner un livreur."
            for g in _get_gestionnaires():
                _create_notif(g, demande, titre, message, 'warning', gestionnaire_url)

    elif new_statut == 'LIVREUR_ROUTE':
        if client:
            _create_notif(
                client, demande,
                "Livreur en route",
                f"Votre livreur est en route pour récupérer votre colis ({ref}).",
                'info', client_url,
            )

    elif new_statut == 'RECEPTION_COLIS':
        if client:
            _create_notif(
                client, demande,
                "Colis récupéré",
                f"Votre colis ({ref}) a été récupéré par le livreur.",
                'success', client_url,
            )
        for g in _get_gestionnaires():
            _create_notif(
                g, demande,
                "Colis pris en charge",
                f"Le livreur a récupéré le colis de la demande {ref}.",
                'info', gestionnaire_url,
            )

    elif new_statut == 'LIVRAISON_EN_ROUTE':
        if client:
            _create_notif(
                client, demande,
                "Livraison en cours",
                f"Votre colis ({ref}) est en cours de livraison vers le destinataire.",
                'info', client_url,
            )

    elif new_statut == 'TERMINEE':
        _liberer_livreur(demande)
        if client:
            _create_notif(
                client, demande,
                "Livraison terminée !",
                f"Votre colis ({ref}) a été livré avec succès.",
                'success', client_url,
            )
        if coursier:
            _create_notif(
                coursier, demande,
                "Course terminée",
                f"La course {ref} est marquée comme terminée. Merci !",
                'success', livreur_url,
            )
        for g in _get_gestionnaires():
            _create_notif(
                g, demande,
                "Livraison effectuée",
                f"La demande {ref} a été livrée avec succès.",
                'success', gestionnaire_url,
            )

    elif new_statut == 'ANNULEE':
        _liberer_livreur(demande)
        if client:
            _create_notif(
                client, demande,
                "Commande annulée",
                f"Votre demande {ref} a été annulée.",
                'danger', client_url,
            )
        if coursier:
            _create_notif(
                coursier, demande,
                "Course annulée",
                f"La course {ref} a été annulée.",
                'warning', livreur_url,
            )
        for g in _get_gestionnaires():
            _create_notif(
                g, demande,
                "Demande annulée",
                f"La demande {ref} a été annulée.",
                'warning', gestionnaire_url,
            )


@receiver(pre_save, sender='Demande.DCL')
def dcl_pre_save(sender, instance, **kwargs):
    """Mémorise le statut précédent avant la sauvegarde."""
    if instance.pk:
        try:
            instance._old_statut = sender.objects.get(pk=instance.pk).statut
        except sender.DoesNotExist:
            instance._old_statut = None
    else:
        instance._old_statut = None


@receiver(post_save, sender='Demande.DCL')
def dcl_post_save(sender, instance, created, update_fields=None, **kwargs):
    """Déclenche les notifications après un changement de statut."""
    # Ignorer si seuls des champs non liés au statut sont mis à jour
    if update_fields is not None and 'statut' not in update_fields:
        return

    if created:
        create_notifications_for_dcl(instance, None, instance.statut)
    else:
        old_statut = getattr(instance, '_old_statut', None)
        if old_statut is not None and old_statut != instance.statut:
            create_notifications_for_dcl(instance, old_statut, instance.statut)
