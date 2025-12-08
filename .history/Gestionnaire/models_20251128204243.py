from django.db import models
from django.utils import timezone
from django_lifecycle import LifecycleModel
import uuid
from safedelete.models import SafeDeleteModel
from Auth.models import CustomUser
 # Modèle de gestionnaire
class Gestionnaire(SafeDeleteModel,LifecycleModel):
    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'gestionnaire'})

    def __str__(self):
        return self.user.username