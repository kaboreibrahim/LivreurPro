from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from Client.views import *


urlpatterns = [

    path('Accueil', Dashbord, name='Dashbord_client'),

] 
