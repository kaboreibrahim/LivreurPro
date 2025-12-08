from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from Gestionnaire.views import *
from Gestionnaire.views.List import ListeDemandesView, DetailDemandeView, changer_statut
from Livreur.views.Dashbord import DashbordLivreur
from Livreur.views.location import update_livreur_location

app_name = 'Livreur'

urlpatterns = [
    # Tableau de bord
    path('Accueil/', DashbordLivreur, name='Dashbord_Livreur'),
    # Mise à jour de la position du livreur
    path('update-location/', update_livreur_location, name='update_livreur_location'),
    
    # Ancienne route commentée
    #path('api/livreur-positions/', get_livreur_positions, name='get_livreur_positions'),
    
    # Redirection de l'URL racine vers le tableau de bord
    path('', RedirectView.as_view(pattern_name='Livreur:Dashbord_Livreur', permanent=False)),
]
