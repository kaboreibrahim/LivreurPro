from urllib import request
from django.db import models
from django.utils import timezone
import uuid
from django.conf import settings
from safedelete.models import SafeDeleteModel
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.files.storage import FileSystemStorage
import os
from django_lifecycle import LifecycleModel
imageFs = FileSystemStorage(location=os.path.join(str(settings.BASE_DIR), '/medias/'))

#### DCL Demande de course en ligne  #####
class DCL(SafeDeleteModel, LifecycleModel):

    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)
    
    # Client qui fait la demande
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='demandes',
        verbose_name="client",
        limit_choices_to={'role': 'client'}
    )
     
    # Informations sur les lieux
    adresse_depart = models.CharField(max_length=255,verbose_name="Adresse de depart")
    adresse_destination = models.CharField(max_length=255,verbose_name="Adresse de destination")
    # Coordonnées GPS (optionnel mais utile pour le suivi)
    latitude_depart = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Latitude de depart  "
    )
    
    longitude_depart = models.FloatField(
     
        null=True, 
        blank=True, 
        verbose_name="Longitude de depart"
    )
    
    latitude_destination = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Latitude de destination"
    )
    
    longitude_destination = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Longitude de destination"
    )
    Contact_destinateur = models.CharField(max_length=255, blank=True, null=True)


    # Informations du colis
    description_colis = models.TextField(
        verbose_name="Description du colis", 
        help_text="Donnez un aperçu détaillé du contenu du colis"
    )
    poids_colis = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Poids du colis (kg)",
        validators=[MinValueValidator(0.01, "Le poids doit être supérieur à 0")]
    )
    valeur_colis = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Valeur du colis (FCFA)",
        validators=[MinValueValidator(0, "La valeur ne peut pas être négative")]
    )
    # Dates
    date_demande = models.DateTimeField(
        default=timezone.now, 
        editable=False, 
        verbose_name="Date de la demande"
    )
    
    date_recuperation = models.DateTimeField(
        verbose_name="Date et heure de récupération",
        help_text="Date souhaitée pour la récupération du colis"
    )
    
    # Type de course : Expresse ou Classique
    TYPE_COURSE_CHOICES = [
        ('EXPRESSE', 'Expresse'),
        ('CLASSIQUE', 'Classique'),
    ]
    type_course = models.CharField(
        max_length=10, choices=TYPE_COURSE_CHOICES, default='CLASSIQUE', verbose_name="Type de course"
    )

    # Statut de la demande
    STATUT_CHOICES = [
            ('EN_ATTENTE', '1. En attente – En attente de proposition de prix vous allez recevoir un appel'),
            ('VALIDATION_CLIENT', '2. Validation client – Le client Valider le prix proposé par le coursier'),
            ('VALIDATION_LIVREUR', '3. Validation livreur – En attente d’acceptation du livreur'),
            ('LIVREUR_ROUTE', '4. Livreur en route pour récupération du colis'),
            ('RECEPTION_COLIS', '5. Récupération du colis'),
            ('LIVRAISON_EN_ROUTE', '6. Livraison en route'),
            ('TERMINEE', '7. Livrée – Livraison terminée'),
            ('ANNULEE', '8. Annulée'),
        ]

    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='EN_ATTENTE', verbose_name="Statut de la demande")
    
    # Coursier
    coursier = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='livraisons',
        verbose_name="Coursier",
        limit_choices_to={'role': 'livreur'}
    )
    
    # Photos du colis
    photo_colis1 = models.ImageField(
        upload_to='photos_colis/%Y/%m/',
        blank=True, 
        null=True, 
        verbose_name="Photo du colis 1",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif'],
                message="Format de fichier non supporté. Utilisez jpg, jpeg, png ou gif."
            )
        ],
        help_text="Téléchargez une photo du colis (max 5 Mo)"
    )
    
    photo_colis2 = models.ImageField(
        upload_to='photos_colis/%Y/%m/',
        blank=True, 
        null=True, 
        verbose_name="Photo du colis 2",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif'],
                message="Format de fichier non supporté. Utilisez jpg, jpeg, png ou gif."
            )
        ],
        help_text="Téléchargez une deuxième photo du colis (optionnel)"
    )
    
    # Informations supplémentaires
    instructions = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Instructions supplémentaires",
        help_text="Toute instruction spécifique pour le livreur"
    )
    
     # Nouveau champ pour la référence unique
    ref = models.CharField(max_length=20, unique=True, editable=False, verbose_name="Référence")
    
    
     # Nouveau champ pour le coût
    cout_livraison = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Coût de livraison"
    )

    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Nouveau champ pour la distance

    class Meta:
        verbose_name = "Demande de coursier"
        verbose_name_plural = "Demandes de coursiers"
        ordering = ['-date_demande']
        
        
    
    
    def get_details(self):
        """Retourne les détails de la demande sous forme de dictionnaire."""
        details = {
            'Référence': self.ref,
            'Client': str(self.client),
            'Adresse départ': self.adresse_depart,
            'Adresse destination': self.adresse_destination,
            'Latitude départ': self.latitude_depart,
            'Longitude départ': self.longitude_depart,
            'Latitude destination': self.latitude_destination,
            'Longitude destination': self.longitude_destination,
            'Contact destinataire': self.Contact_destinateur,
            'Description colis': self.description_colis,
            'Poids colis': self.poids_colis,
            'Valeur colis': self.valeur_colis,
            'Date demande': self.date_demande.strftime('%Y-%m-%d %H:%M:%S'),
            'Date récupération': self.date_recuperation.strftime('%Y-%m-%d %H:%M:%S'),
            'Type de course': dict(self.TYPE_COURSE_CHOICES).get(self.type_course),
            'Statut': dict(self.STATUT_CHOICES).get(self.statut),
            'Coursier': str(self.coursier) if self.coursier else 'Non attribué',
            'Instructions supplémentaires': self.instructions or 'Aucune instruction',
            'Photos colis': [self.photo_colis1.url if self.photo_colis1 else 'Aucune', 
                            self.photo_colis2.url if self.photo_colis2 else 'Aucune'],
        }
        return details
    
    
    def get_roadmap_html(self):
        """Retourne la roadmap visuelle de la demande."""
        etapes = [
            ('EN_ATTENTE', 'En attente de validation', 'Votre demande est en attente de validation.'),
            ('VALIDATION_CLIENT', 'Validation client', 'En attente de validation du prix par le client.'),
            ('VALIDATION_LIVREUR', 'Validation livreur', 'En attente de validation par un livreur.'),
            ('LIVREUR_ROUTE', 'Livreur en route', 'Un livreur a été assigné et se dirige vers le point de collecte.'),
            ('RECEPTION_COLIS', 'Colis récupéré', 'Le livreur a récupéré votre colis.'),
            ('LIVRAISON_EN_ROUTE', 'En cours de livraison', 'Votre colis est en cours de livraison.'),
            ('TERMINEE', 'Livraison terminée', 'Votre colis a été livré avec succès.'),
            ('ANNULEE', 'Commande annulée', 'Cette commande a été annulée.')
        ]

        # Trouver l'index de l'étape actuelle
        current_index = next((i for i, (status, _, _) in enumerate(etapes) if status == self.statut), -1)
        
        html = '<div class="timeline">'
        
        for i, (status, title, description) in enumerate(etapes):
            # Déterminer la classe en fonction de l'état
            if i < current_index:
                status_class = 'completed'
                icon = '<i class="bi bi-check-circle-fill"></i>'
            elif i == current_index:
                status_class = 'current'
                icon = '<i class="bi bi-arrow-right-circle-fill"></i>'
            else:
                status_class = 'pending'
                icon = '<i class="bi bi-circle"></i>'
            
            # Ajouter la classe 'last' pour le dernier élément
            last_class = 'last' if i == len(etapes) - 1 else ''
            
            html += f'''
            <div class="timeline-step {status_class} {last_class}">
                <div class="timeline-icon">
                    {icon}
                </div>
                <div class="timeline-content">
                    <h4>{title}</h4>
                    <p>{description}</p>
                </div>
            </div>
            '''
        
        html += '</div>'
        
        return f'''
        <style>
            .timeline {
                position: relative;
                padding: 20px 0;
            }
            .timeline::before {
                content: '';
                position: absolute;
                left: 20px;
                top: 0;
                bottom: 0;
                width: 2px;
                background: #e9ecef;
            }
            .timeline-step {
                position: relative;
                padding-left: 50px;
                margin-bottom: 30px;
            }
            .timeline-step:last-child {
                margin-bottom: 0;
            }
            .timeline-icon {
                position: absolute;
                left: 0;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                background: white;
                border: 2px solid #e9ecef;
                color: #6c757d;
            }
            .timeline-step.completed .timeline-icon {
                background-color: #198754;
                border-color: #198754;
                color: white;
            }
            .timeline-step.current .timeline-icon {
                background-color: #0d6efd;
                border-color: #0d6efd;
                color: white;
                animation: pulse 2s infinite;
            }
            .timeline-content {
                padding: 15px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .timeline-step.completed .timeline-content {
                border-left: 3px solid #198754;
            }
            .timeline-step.current .timeline-content {
                border-left: 3px solid #0d6efd;
            }
            .timeline-content h4 {
                margin: 0 0 5px 0;
                color: #212529;
            }
            .timeline-content p {
                margin: 0;
                color: #6c757d;
                font-size: 0.9em;
            }
           
        </style>
        {html}
        '''


    def __str__(self):
        return f"Demande #{self.ref} | Client: {self.client} | Statut: {self.get_statut_display()}"

    
 

    def save(self, *args, **kwargs):
        if not self.ref:
            # Générer une référence unique basée sur un UUID
            self.ref = f'DCL-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    def update_status(self, new_status):
        if new_status in dict(self.STATUT_CHOICES):
            self.statut = new_status
            self.save()

    def calculate_distance(self):
        """
        Calcule la distance en kilomètres entre le port et la localité en utilisant l'API Mapbox
        et met à jour le champ distance.
        Retourne la distance calculée ou None en cas d'erreur.
        """
        import requests
        from django.conf import settings
        
        # Vérifier que les coordonnées existent
        if not all([self.latitude_depart, self.longitude_depart, 
                   self.latitude_destination, self.longitude_destination]):
            return None
            
        # Récupérer le token Mapbox depuis les paramètres
        mapbox_token = getattr(settings, 'MAPBOX_ACCESS_TOKEN', '')
        if not mapbox_token:
            return None
            
        # Coordonnées au format lon,lat pour Mapbox
        origin = f"{self.longitude_depart},{self.latitude_depart}"
        destination = f"{self.longitude_destination},{self.latitude_destination}"
        
        # URL de l'API Mapbox Matrix
        url = (
            f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving/"
            f"{origin};{destination}?access_token={mapbox_token}&annotations=distance"
        )
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # La distance est en mètres, on convertit en kilomètres
                distance_km = data['distances'][0][1] / 1000
                self.distance = round(distance_km, 2)
                self.save(update_fields=['distance'])
                return self.distance
        except (requests.RequestException, KeyError, IndexError) as e:
            # En cas d'erreur, on ne fait rien et on retourne None
            pass
            
        return None