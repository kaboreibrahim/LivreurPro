from django.urls import path
from . import views

urlpatterns = [
    path('demande/nouvelle/', views.creer_demande_livraison, name='creer_demande'),
     
]