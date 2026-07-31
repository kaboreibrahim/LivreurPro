from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from Gestionnaire.views import *
from Gestionnaire.views.assigner import assigner_livreur_modal, assigner_livreur
from Gestionnaire.views.pdf import recu_pdf_gestionnaire
from Gestionnaire.views.facture import facture_pdf, generer_facture, facture_livraison_manuelle_pdf
from Gestionnaire.views.livraison_manuelle import (
    LivraisonManuelleListView, creer_livraison_manuelle,
    modifier_livraison_manuelle, supprimer_livraison_manuelle,
)

app_name = 'Gestionnaire'

urlpatterns = [
    # Tableau de bord
    path('Accueil/', DashbordGestionnaire, name='Dashbord_Gestionnaire'),
    
    # Gestion des demandes
    path('demandes/', ListeDemandesView.as_view(), name='liste_demandes_gestionnaire'),
    path('demandes/<uuid:pk>/', DetailDemandeView.as_view(), name='detail_demande'),
    path('demandes/<uuid:pk>/modifier-prix/', modifier_prix, name='modifier_prix'),
    path('demandes/<uuid:demande_id>/assigner-livreur/modal/', assigner_livreur_modal, name='assigner_livreur_modal'),
    path('demandes/<uuid:demande_id>/assigner-livreur/', assigner_livreur, name='assigner_livreur'),
    
    # Changement de statut
    path('demandes/<uuid:pk>/statut/<str:nouveau_statut>/', changer_statut, name='changer_statut'),
    path('demandes/<uuid:pk>/recu-pdf/', recu_pdf_gestionnaire, name='recu_pdf'),
    path('demandes/<uuid:pk>/facture-pdf/', facture_pdf, name='facture_pdf'),
    path('demandes/<uuid:pk>/generer-facture/', generer_facture, name='generer_facture'),

    # localisatoion des livreurs
    path('api/livreur-positions/', get_livreur_positions, name='get_livreur_positions'),
    path('livreurs/Disponible', LivreurDisponible.as_view(), name='livreur_disponible'),

    # Gestion des clients
    path('clients/', ListeClientsView.as_view(), name='liste_clients'),
    path('clients/<int:pk>/', DetailClientView.as_view(), name='detail_client'),
    path('clients/<int:pk>/activer-desactiver/', activer_desactiver_client, name='activer_desactiver_client'),

    # Registre des livraisons manuelles (clients récurrents/B2B hors workflow DCL)
    path('livraisons-manuelles/', LivraisonManuelleListView.as_view(), name='livraisons_manuelles_liste'),
    path('livraisons-manuelles/creer/', creer_livraison_manuelle, name='creer_livraison_manuelle'),
    path('livraisons-manuelles/<uuid:pk>/modifier/', modifier_livraison_manuelle, name='modifier_livraison_manuelle'),
    path('livraisons-manuelles/<uuid:pk>/supprimer/', supprimer_livraison_manuelle, name='supprimer_livraison_manuelle'),
    path('livraisons-manuelles/<uuid:pk>/facture-pdf/', facture_livraison_manuelle_pdf, name='facture_livraison_manuelle_pdf'),


    # Redirection de l'URL racine vers le tableau de bord
    path('', RedirectView.as_view(pattern_name='Gestionnaire:get_livreur_positions', permanent=False)),
]
