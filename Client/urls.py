from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from Client.views import *
from Client.views.history import commande_history, commande_detail
from Client.views.accepter import accepter_prix
from Client.views.confirmer import confirmer_recuperation
from Client.views.pdf import recu_pdf

app_name = 'Client'
urlpatterns = [

    path('Accueil/', dashboard, name='Dashbord_client'),
    path('demande/nouvelle/', creer_demande_livraison, name='creer_demande'),
    path('demandes/', liste_demandes, name='liste_demandes'),
    path('demande/<uuid:pk>/', detail_demande, name='detail_demande'),
    path('demande/<uuid:pk>/accepter-prix/', accepter_prix, name='accepter_prix'),
    path('demande/<uuid:pk>/confirmer-recuperation/', confirmer_recuperation, name='confirmer_recuperation'),
    path('demande/<uuid:pk>/recu-pdf/', recu_pdf, name='recu_pdf'),
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
