import json
import logging

from django.conf import settings
from pywebpush import WebPushException, webpush

logger = logging.getLogger(__name__)


def send_push_to_subscription(subscription, payload):
    """Envoie une notification push à un abonnement unique.

    `payload` est un dict JSON-sérialisable (title, body, icon, badge, image,
    url, tag, renotify, timestamp, actions — voir service-worker.js).

    Retourne True si l'envoi a réussi. Si le service de push répond que
    l'abonnement n'existe plus (404/410), le désactive automatiquement et
    retourne False — c'est le mécanisme de nettoyage des abonnements invalides.
    """
    try:
        webpush(
            subscription_info=subscription.subscription_info,
            data=json.dumps(payload),
            vapid_private_key=settings.VAPID_PRIVATE_KEY_PATH,
            vapid_claims={'sub': f'mailto:{settings.VAPID_ADMIN_EMAIL}'},
        )
        return True
    except WebPushException as exc:
        status_code = exc.response.status_code if exc.response is not None else None
        if status_code in (404, 410):
            subscription.actif = False
            subscription.save(update_fields=['actif'])
            logger.info("Abonnement push expiré, désactivé: %s", subscription.endpoint)
        else:
            logger.warning("Échec d'envoi push (%s): %s", status_code, exc)
        return False
