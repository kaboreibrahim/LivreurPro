from urllib import request
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import os
from django_lifecycle import LifecycleModel
import uuid
from django.utils.timezone import now
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

imageFs = FileSystemStorage(location=os.path.join(str(settings.BASE_DIR), '/medias/'))
# Modèle d'utilisateur personnalisé
class CustomUser(AbstractUser,SafeDeleteModel):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('livreur', 'Livreur'),
        ('gestionnaire', 'Gestionnaire'),
    )
    
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='client')
    Contact = models.CharField(max_length=20)
    photos = models.ImageField("Photo", upload_to='Proprietaire_photos/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
    is_online = models.BooleanField(default=False)  # champ pour le statut en ligne
    last_login= 
    # Ajout de related_name pour éviter les conflits
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        related_query_name='customuser',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        related_query_name='customuser',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    def __str__(self):
        return f"{self.username}"

    # Signaux pour mettre à jour le statut en ligne et la date de dernière connexion
    @receiver(user_logged_in)
    def user_logged_in_handler(sender, request, user, **kwargs):
        user.is_online = True
        user.last_login = timezone.now()  # Met à jour le champ last_login
        user.save()

    @receiver(user_logged_out)
    def user_logged_out_handler(sender, request, user, **kwargs):
        user.is_online = False
        user.save()

# Modele de verificacion
class VerificationCode(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.code}"
    
 