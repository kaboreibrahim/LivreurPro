from django.contrib import admin
from django.utils.html import format_html
from .models import Livreur


@admin.action(description="Marquer comme LIBRE")
def mark_as_free(modeladmin, request, queryset):
    queryset.update(is_available='LIBRE')
    modeladmin.message_user(request, "Les livreurs sélectionnés sont maintenant LIBRES.")


@admin.action(description="Marquer comme OCCUPÉ")
def mark_as_busy(modeladmin, request, queryset):
    queryset.update(is_available='OCCUPER')
    modeladmin.message_user(request, "Les livreurs sélectionnés sont maintenant OCCUPÉS.")


class LivreurAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "username",
        "role",
        "is_available",
        "adresse",
        "latitude",
        "longitude",
        "date_mise_a_jour_coordonnees",
        "date_sauvegarde_coordonnees",
    )

    search_fields = ("user__username", "user__email", "adresse")
    list_filter = ("is_available", "user__role")
    ordering = ("-date_mise_a_jour_coordonnees",)
    readonly_fields = (
        "id",
        "date_mise_a_jour_coordonnees",
        "date_sauvegarde_coordonnees",
    )
    actions = [mark_as_free, mark_as_busy]

    # Champs dans les formulaires Admin
    fieldsets = (
        ("Information utilisateur", {
            "fields": ("id", "user", "is_available", "role_display")
        }),
        ("Localisation", {
            "fields": ("latitude", "longitude", "adresse")
        }),
        ("Dates automatiques", {
            "fields": ("date_mise_a_jour_coordonnees", "date_sauvegarde_coordonnees")
        }),
    )

    # Affichage du rôle (utile quand tu fais des filtres)
    def role(self, obj):
        return obj.user.role
    role.short_description = "Rôle"

    # Affichage du username
    def username(self, obj):
        return obj.user.username
    username.short_description = "Nom d'utilisateur"

    # Champ non modifiable juste pour l’affichage
    def role_display(self, obj):
        return obj.user.role
    role_display.short_description = "Rôle (non modifiable)"


admin.site.register(Livreur, LivreurAdmin)
