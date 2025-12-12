from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from Client.views import *
from Client.views.history import commande_history, commande_detail

app_name = 'Client'
urlpatterns = [

    path('Accueil/', Dashbord, name='Dashbord_client'),
    path('demande/nouvelle/', creer_demande_livraison, name='creer_demande'),
    path('demandes/', liste_demandes, name='liste_demandes'),
    path('demande/<uuid:pk>/', detail_demande, name='detail_demande'),
    path('non-autorise/', non_autorise, name='non_autorise'),

    

    ################# Profil client #################
      # Profil client
    path('profile', profile, name='profile'),
    path('profile/commande/<str:ref>/annuler/', annuler_commande, name='annuler_commande'),



    path('profil/modifier/', edit_profile, name='edit_profile'),
    path('profil/mot-de-passe/', change_password, name='change_password'),
    path('profil/parametres/', parametres, name='parametres'),
    
    # Historique des commandes
    path('commandes/historique/', commande_history, name='commande_history'),
    path('commandes/<str:ref>/', commande_detail, name='commande_detail'),

] 
