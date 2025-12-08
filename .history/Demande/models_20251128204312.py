
class DemandeCoursier(SafeDeleteModel, LifecycleModel):

    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)
    
    # Client qui fait la demande
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='demandes',
        verbose_name="client",
        limit_choices_to={'role': 'client'}
    )
    nom_client = models.CharField(max_length=255, blank=True, null=True)
    numero_client = models.CharField(max_length=255, blank=True, null=True)
    
    # Informations sur les lieux
    adresse_depart = models.CharField(max_length=255)
    adresse_destination = models.CharField(max_length=255)
    # Coordonnées GPS (optionnel mais utile pour le suivi)
    latitude_depart = models.DecimalField(
        max_digits=6, 
        decimal_places=5, 
        null=True, 
        blank=True, 
        verbose_name="Latitude de départ"
    )
    
    longitude_depart = models.DecimalField(
       max_digits=6, 
        decimal_places=5, 
        null=True, 
        blank=True, 
        verbose_name="Longitude de départ"
    )
    
    latitude_destination = models.DecimalField(
        max_digits=6, 
        decimal_places=5, 
        null=True, 
        blank=True, 
        verbose_name="Latitude de destination"
    )
    
    longitude_destination = models.DecimalField(
        max_digits=6, 
        decimal_places=5, 
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
        ('EN_ATTENTE', 'En attente'),
        ('EN_ATTENTE_VALIDATION_CLIENT', 'En attente validation client'),
        ('PRIX_VALIDE_PAR_CLIENT', 'Prix validé par le client'),
        ('EN_ATTENTE_DE_LIVREUR', 'En attente de livreur'),
        ('LIVREUR_EN_ROUTE', 'Livreur en route'),
        ('RECEPTION', 'Réception du colis'),
        ('LIVRAISON_EN_COURS', 'Livraison en cours'),
        ('TERMINEE', 'Terminée'),
        ('ANNULEE', 'Annulée'),
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
    
    
    def get_roadmap(self):
        """Retourne la roadmap de la demande en fonction de son statut."""
        roadmap = []

        # Liste des étapes avec leur statut et description - MISE À JOUR
        etapes = [
            ('EN_ATTENTE', "1. Demande en attente - En attente de proposition de prix."),
            ('EN_ATTENTE_VALIDATION_CLIENT', "2. Prix proposé - En attente de validation du client."),
            ('PRIX_VALIDE_PAR_CLIENT', "3. Prix validé - En attente d'affectation d'un livreur."),
            ('EN_ATTENTE_DE_LIVREUR', "4. Livreur affecté - En attente de validation du livreur."),
            ('LIVREUR_EN_ROUTE', "5. Livreur en route - Le coursier est en chemin pour récupérer le colis."),
            ('RECEPTION', "6. Colis réceptionné - Le livreur a récupéré votre colis."),
            ('LIVRAISON_EN_COURS', "7. Livraison en cours - Le coursier est en train de livrer le colis."),
            ('TERMINEE', "8. Livraison terminée - Le colis a été livré avec succès."),
        ]

        # Trouver l'index de l'étape actuelle
        statut_index = next((index for index, (statut, _) in enumerate(etapes) if statut == self.statut), -1)

        # Construire la roadmap en marquant les étapes
        for index, (_, description) in enumerate(etapes):
            if index <= statut_index:
                roadmap.append(f"✅ {description}")  # Marquer les étapes terminées
            else:
                roadmap.append(f"⬜ {description}")  # Étapes non atteintes

        return '\n'.join(roadmap)


    def __str__(self):
        return f"Demande #{self.ref} | Client: {self.client} | Statut: {self.get_statut_display()}"

    
 

    def save(self, *args, **kwargs):
        if not self.ref:
            # Générer une référence unique basée sur un UUID
            self.ref = f'DC-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    def update_status(self, new_status):
        if new_status in dict(self.STATUT_CHOICES):
            self.statut = new_status
            self.save()