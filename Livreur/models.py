from django.db import models
from django.utils import timezone
from django_lifecycle import LifecycleModel
import uuid
from safedelete.models import SafeDeleteModel
from Auth.models import CustomUser
 # Modèle de livreur
class Livreur(SafeDeleteModel, LifecycleModel):
    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'livreur'})
    latitude =models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Latitude "
    )
    longitude = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Longitude "
    )
    is_available = models.CharField(max_length=10, choices=[('OCCUPER', 'OCCUPER'), ('LIBRE', 'LIBRE')], default='LIBRE')
    adresse = models.CharField(max_length=255, null=True, blank=True)
    date_mise_a_jour_coordonnees = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour des coordonnées")
    date_sauvegarde_coordonnees = models.DateTimeField(null=True, blank=True, verbose_name="Date de sauvegarde des coordonnées")

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self.date_mise_a_jour_coordonnees = timezone.now()
            self.date_sauvegarde_coordonnees = timezone.now()
        super().save(*args, **kwargs)
