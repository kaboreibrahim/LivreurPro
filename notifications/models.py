from django.conf import settings
from django.db import models


class PushSubscription(models.Model):
    """Abonnement Web Push d'un navigateur pour un utilisateur donné."""

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
        verbose_name="Utilisateur",
    )
    endpoint = models.URLField(max_length=500, unique=True, verbose_name="Endpoint")
    p256dh = models.CharField(max_length=255, verbose_name="Clé p256dh")
    auth = models.CharField(max_length=255, verbose_name="Clé auth")
    user_agent = models.CharField(max_length=500, blank=True, verbose_name="User-Agent")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Abonnement Push"
        verbose_name_plural = "Abonnements Push"

    def __str__(self):
        return f"{self.utilisateur} — {self.endpoint[:60]}"

    @property
    def subscription_info(self):
        """Format attendu par pywebpush.webpush()."""
        return {
            'endpoint': self.endpoint,
            'keys': {
                'p256dh': self.p256dh,
                'auth': self.auth,
            },
        }
