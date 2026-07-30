from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from Livreur.views.Dashbord import DashbordLivreur
from Livreur.views.location import update_livreur_location
from Livreur.views.list import DemandeLivreurListView
from Livreur.views.detail import detail_demande_livreur
from Livreur.views.accepter import accepter_course
from Livreur.views.livraison import commencer_livraison, confirmer_livraison, confirmer_recuperation_expediteur
app_name = 'Livreur'

urlpatterns = [
    # Tableau de bord
    path('Accueil/', DashbordLivreur, name='Dashbord_Livreur'),
    # Mise à jour de la position du livreur
    path('update-location/', update_livreur_location, name='update_livreur_location'),

    path('mes-demandes/', DemandeLivreurListView.as_view(), name='livreur_demandes_liste'),

    path('detail/course/<uuid:pk>/', detail_demande_livreur, name='detail_demande_livreur'),
    path('detail/course/<uuid:pk>/accepter/', accepter_course, name='accepter_course'),
    path('detail/course/<uuid:pk>/confirmer-recuperation/', confirmer_recuperation_expediteur, name='confirmer_recuperation_expediteur'),
    path('detail/course/<uuid:pk>/commencer-livraison/', commencer_livraison, name='commencer_livraison'),
    path('detail/course/<uuid:pk>/confirmer-livraison/', confirmer_livraison, name='confirmer_livraison'),
    
    # Redirection de l'URL racine vers le tableau de bord
    path('', RedirectView.as_view(pattern_name='Livreur:update_livreur_location', permanent=False)),
]
