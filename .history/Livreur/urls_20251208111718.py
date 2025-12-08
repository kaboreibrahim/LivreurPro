from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from Livreur.views.Dashbord import DashbordLivreur
from Livreur.views.location import update_livreur_location
from Livreur.views.list import DemandeLivreurListView
from Livreur.views.detail import detail_demande_livreur
app_name = 'Livreur'

urlpatterns = [
    # Tableau de bord
    path('Accueil/', DashbordLivreur, name='Dashbord_Livreur'),
    # Mise à jour de la position du livreur
    path('update-location/', update_livreur_location, name='update_livreur_location'),
    
    path('mes-demandes/', DemandeLivreurListView.as_view(), name='livreur_demandes_liste'),

    path('detail/course/<int:pk>/', detail_demande_livreur, name='detail_demande_livreur'),
    
    # Redirection de l'URL racine vers le tableau de bord
    path('', RedirectView.as_view(pattern_name='Livreur:update_livreur_location', permanent=False)),
]
