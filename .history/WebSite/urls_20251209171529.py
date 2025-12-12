from ast import pattern
from django.urls import path
from django.views.generic import RedirectView,TemplateView
from django.contrib.auth import views as auth_views
from WebSite.views import *

urlpatterns = [
        path('', RedirectView.as_view(url='accueil/')),
        path('accueil/', home, name='Accueil'),
        path('service/',service,name='Service'),
        path('apropos/',apropos,name='Apropos'),
        path('contact/',contact,name='Contact'),   
        path('robots.txt', robots_txt, name='robots_txt'),
        path('sitemap.xml', TemplateView.as_view(template_name='pages/sitemap.xml', content_type='application/xml')),


] 
