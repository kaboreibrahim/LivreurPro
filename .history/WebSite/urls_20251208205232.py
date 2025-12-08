from ast import pattern
from django.urls import path
from django.views.generic import RedirectView,TemplateView
from django.contrib.auth import views as auth_views
from WebSite.views import *

urlpatterns = [
        path('', RedirectView.as_view(url='accueil/monlivreurpro', permanent=False)),
        path('accueil/monlivreurpro/', home, name='Accueil'),
        path('service/monlivreurpro/',service,name='Service'),
        path('apropos/monlivreurpro/',apropos,name='Apropos'),
        path('contact/monlivreurpro/',contact,name='Contact'),   
        path('robots.txt', robots_txt, name='robots_txt'),
        path('sitemap.xml', TemplateView.as_view(template_name='pages/sitemap.xml', content_type='application/xml')),


] 
