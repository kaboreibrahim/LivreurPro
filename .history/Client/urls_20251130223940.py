from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from Client.views import *
from Client.decorators import role_required

app_name = 'Client'

urlpatterns = [
    path('Accueil/', role_required("client")(Dashbord), name='Dashbord_client'),
    path('demande/nouvelle/', role_required("client")(creer_demande_livraison), name='creer_demande'),
    path('demandes/', role_required("client")(liste_demandes), name='liste_demandes'),
    path('demande/<uuid:pk>/', role_required("client")(detail_demande), name='detail_demande'),

    # Page "Accès refusé"
    path('non-autorise/', non_autorise, name='non_autorise'),
] 