from ast import pattern
from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from website.views import *

urlpatterns = [
        path('', RedirectView.as_view(url='accueil/monlivreurpro', permanent=False)),
        path('accueil/monlivreurpro/', home, name='Accueil'),
        path('service/monlivreurpro/',service,name='Service'),
        path('apropos/monlivreurpro/',apropos,name='Apropos'),
        path('contact/monlivreurpro/',contact,name='Contact'),   
] 

handler404 = 'website.views.error.custom_404_view'
handler500 = 'website.views.error.custom_500_view'
