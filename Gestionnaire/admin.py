from django.contrib import admin
from .models import Gestionnaire, LivraisonManuelle


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


@admin.register(LivraisonManuelle)
class LivraisonManuelleAdmin(admin.ModelAdmin):
    list_display = ('date_livraison', 'client_nom', 'nature_colis', 'lieu_depart', 'lieu_arrivee', 'montant', 'numero_facture')
    search_fields = ('client_nom', 'client_telephone', 'nature_colis')
    list_filter = ('date_livraison',)
    readonly_fields = ('id', 'numero_facture', 'date_facture')
