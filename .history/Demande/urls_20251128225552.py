from django.urls import path
from . import views

urlpatterns = [
    path('demande/nouvelle/', creer_demande_livraison, name='creer_demande'),
     
]