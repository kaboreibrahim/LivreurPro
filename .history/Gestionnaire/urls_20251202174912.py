from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from Gestionnaire.views import *
 
app_name = 'Gestionnaire'

urlpatterns = [
    # Tableau de bord
    path('Accueil/', DashbordGestionnaire, name='Dashbord_Gestionnaire'),
    
    # Gestion des demandes
    path('demandes/', ListeDemandesView.as_view(), name='liste_demandes_gestionnaire'),
    path('demandes/<uuid:pk>/', DetailDemandeView.as_view(), name='detail_demande'),
    path('demandes/<uuid:pk>/modifier-prix/', modifier_prix, name='modifier_prix'),
    
    # localisatoion des livreurs
    path('api/livreur-positions/', get_livreur_positions, name='get_livreur_positions'),
    path('livreurs/Disponible', LivreurDisponible.as_view(), name='livreur_disponible'),

    # Gestion des clients
    path('clients/', ListeClientsView.as_view(), name='liste_clients'),
    # path('clients/<int:pk>/', DetailClientView.as_view(), name='detail_client'),
    # path('clients/<int:pk>/activer-desactiver/', activer_desactiver_client, name='activer_desactiver_client'),


    # Redirection de l'URL racine vers le tableau de bord
    path('', RedirectView.as_view(pattern_name='Gestionnaire:get_livreur_positions', permanent=False)),
]
