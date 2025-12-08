from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from Auth.views import *
urlpatterns = [
        path('Accueil/client', index_client, name='index_client'),
        path('Accueil/livreur/', index_livreur, name='index_livreur'),
        path('Accueil/gestionnaire', index_gestionnaire, name='index_gestionnaire'),
        
        ### view de connexion
        path('register/', register, name='register'),
        path('login/', user_login, name='login'),
        path('deconnexion',deconnection,name='deconnexion'),
        path('verify/', verify, name='verify'),
        
          #view de recuperation de compte 
        path('reset-password/', CustomPasswordResetView.as_view(), name='password_reset'),
        path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/rest/password_reset_done.html'), name='password_reset_done'),
        path('reset-password/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/rest/password_reset_confirm.html'), name='password_reset_confirm'),
        path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/rest/password_reset_complete.html'), name='password_reset_complete'),
] 
