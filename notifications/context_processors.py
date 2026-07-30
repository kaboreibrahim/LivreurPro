from django.conf import settings


def vapid_context(request):
    return {'vapid_public_key': settings.VAPID_PUBLIC_KEY}
