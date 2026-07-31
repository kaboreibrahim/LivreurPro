from django.db import models
from django.utils import timezone
from django_lifecycle import LifecycleModel
import uuid
from safedelete.models import SafeDeleteModel
from django.core.validators import MinValueValidator
from Auth.models import CustomUser
 # Modèle de gestionnaire
class Gestionnaire(SafeDeleteModel,LifecycleModel):
    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'gestionnaire'})

    def __str__(self):
        return self.user.username


class LivraisonManuelle(SafeDeleteModel, LifecycleModel):
    """Registre des livraisons de clients récurrents/B2B suivies hors du workflow
    DCL (pas de compte client, pas de statut livreur/GPS) — anciennement tenu
    dans un tableur externe. Facturable indépendamment, une ligne = une facture.
    """
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)

    date_livraison = models.DateField(verbose_name="Date")
    client_nom = models.CharField(max_length=150, verbose_name="Client")
    client_telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Numéro client")
    nature_colis = models.CharField(max_length=255, verbose_name="Nature du colis")
    lieu_depart = models.CharField(max_length=255, verbose_name="Départ")
    lieu_arrivee = models.CharField(max_length=255, verbose_name="Arrivée")
    observations = models.CharField(max_length=255, blank=True, null=True, verbose_name="Observations")
    montant = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Montant (FCFA)",
        validators=[MinValueValidator(0)]
    )

    cree_par = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='livraisons_manuelles_creees'
    )
    date_creation = models.DateTimeField(default=timezone.now, editable=False)

    # Facturation définitive — même schéma que DCL, séquence partagée
    # (voir Demande.models.assign_numero_facture)
    numero_facture = models.CharField(max_length=30, unique=True, null=True, blank=True, verbose_name="Numéro de facture")
    date_facture = models.DateTimeField(null=True, blank=True, verbose_name="Date de facturation")

    class Meta:
        verbose_name = "Livraison manuelle"
        verbose_name_plural = "Livraisons manuelles"
        ordering = ['-date_livraison', '-date_creation']

    def __str__(self):
        return f"{self.client_nom} — {self.date_livraison} ({self.lieu_depart} → {self.lieu_arrivee})"

    def get_designation_facture(self):
        return f"{self.nature_colis} — {self.lieu_depart} → {self.lieu_arrivee}"

    def get_or_create_numero_facture(self):
        from Demande.models import assign_numero_facture
        return assign_numero_facture(self)