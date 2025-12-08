from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from Gestionnaire.views import *
from Gestionnaire.views.List import ListeDemandesView, DetailDemandeView, changer_statut
from Livreur.views.Dashbord import DashbordLivreur

app_name = 'Livreur'

urlpatterns = [
    # Tableau de bord
    path('Accueil/', DashbordLivreur, name='Dashbord_Livreur'),
    # Positions des livreurs (API)
    "path('api/livreur-positions/', get_livreur_positions, name='get_livreur_positions'),
     
    
    # Redirection de l'URL racine vers le tableau de bord
    path('', RedirectView.as_view(pattern_name='Livreur:Dashbord_Livreur', permanent=False)),
]
