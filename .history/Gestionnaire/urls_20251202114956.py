from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from Gestionnaire.views import *
from Gestionnaire.views.List import ListeDemandesView, DetailDemandeView

app_name = 'Gestionnaire'

urlpatterns = [
    # Tableau de bord
    path('Accueil/', DashbordGestionnaire, name='Dashbord_Gestionnaire'),
    
    # Gestion des demandes
    path('demandes/', ListeDemandesView.as_view(), name='liste_demandes_gestionnaire'),
    path('demandes/<uuid:pk>/', DetailDemandeView.as_view(), name='detail_demande'),
    path('demandes/<uuid:pk>/modifier-prix/', modifier_prix, name='modifier_prix'),
    
    # Ancienne route commentée
    path('api/livreur-positions/', get_livreur_positions, name='get_livreur_positions'),


    # Redirection de l'URL racine vers le tableau de bord
    path('', RedirectView.as_view(pattern_name='Gestionnaire:Dashbord_Gestionnaire', permanent=False)),
]
