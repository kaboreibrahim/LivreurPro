from django.contrib import admin
from .models import Gestionnaire


class GestionnaireAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "username", "role")
    search_fields = ("user__username", "user__email")
    list_filter = ("user__role",)
    readonly_fields = ("id",)

    def username(self, obj):
        return obj.user.username
    username.short_description = "Nom d'utilisateur"

    def role(self, obj):
        return obj.user.role
    role.short_description = "Rôle"


admin.site.register(Gestionnaire, GestionnaireAdmin)
