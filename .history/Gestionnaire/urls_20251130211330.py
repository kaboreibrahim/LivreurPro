from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from Gestionnaire.views import *

app_name = 'Gestionnaire'
urlpatterns = [

    path('Accueil/Gestionnaire/', DashbordGestionnaire, name='Dashbord_Gestionnaire'),
     
] 
