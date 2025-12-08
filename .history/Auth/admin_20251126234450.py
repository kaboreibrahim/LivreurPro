from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, VerificationCode, Livreur, Gestionnaire

# Admin pour le modèle CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'Contact', 'is_verified', 'is_online', 'Date_ajout')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'Contact', 'photos', 'is_verified', 'is_online')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'Contact', 'photos', 'is_verified', 'is_online')}),
    )
