from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from Gestionnaire.views import *
from Gestionnaire.views.List import ListeDemandesView, DetailDemandeView, changer_statut

app_name = 'Gestionnaire'

urlpatterns = [
    # Tableau de bord
    path('Accueil/', DashbordGestionnaire, name='Dashbord_Gestionnaire'),
    
    # Gestion des demandes
    path('demandes/', ListeDemandesView.as_view(), name='liste_demandes'),
    path('demandes/<uuid:pk>/', DetailDemandeView.as_view(), name='detail_demande'),
    path('demandes/<uuid:pk>/changer-statut/<str:nouveau_statut>/', changer_statut, name='changer_statut'),
    
    # Redirection de l'URL racine vers le tableau de bord
    path('', RedirectView.as_view(pattern_name='Gestionnaire:Dashbord_Gestionnaire', permanent=False)),
]
