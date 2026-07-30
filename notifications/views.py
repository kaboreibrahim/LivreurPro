import json
from urllib.parse import urlparse

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import PushSubscription

# Domaines connus des services de push des navigateurs — évite l'enregistrement
# d'endpoints arbitraires/falsifiés (Chrome/Edge/Brave, Firefox, Safari, anciens Edge/IE).
ALLOWED_PUSH_HOST_SUFFIXES = (
    'fcm.googleapis.com',
    'android.googleapis.com',
    'updates.push.services.mozilla.com',
    'notify.windows.com',
    'push.apple.com',
)


def _endpoint_is_trusted(endpoint):
    try:
        parsed = urlparse(endpoint)
    except ValueError:
        return False
    if parsed.scheme != 'https' or not parsed.hostname:
        return False
    host = parsed.hostname
    return any(host == suffix or host.endswith('.' + suffix) for suffix in ALLOWED_PUSH_HOST_SUFFIXES)


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return None


@login_required
@require_POST
def subscribe(request):
    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({'error': 'JSON invalide'}, status=400)

    endpoint = payload.get('endpoint')
    keys = payload.get('keys') or {}
    p256dh = keys.get('p256dh')
    auth = keys.get('auth')
    old_endpoint = payload.get('old_endpoint')

    if not endpoint or not p256dh or not auth:
        return JsonResponse({'error': 'Champs manquants'}, status=400)

    if not _endpoint_is_trusted(endpoint):
        return JsonResponse({'error': "Endpoint de push non reconnu"}, status=400)

    if old_endpoint and old_endpoint != endpoint:
        PushSubscription.objects.filter(utilisateur=request.user, endpoint=old_endpoint).delete()

    PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={
            'utilisateur': request.user,
            'p256dh': p256dh,
            'auth': auth,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
            'actif': True,
        },
    )
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def unsubscribe(request):
    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({'error': 'JSON invalide'}, status=400)

    endpoint = payload.get('endpoint')
    if not endpoint:
        return JsonResponse({'error': 'Endpoint manquant'}, status=400)

    PushSubscription.objects.filter(utilisateur=request.user, endpoint=endpoint).delete()
    return JsonResponse({'status': 'ok'})
