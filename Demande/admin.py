from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import DCL, ClientInvite
import uuid


@admin.register(ClientInvite)
class ClientInviteAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'telephone', 'email', 'created_at')
    search_fields = ('nom', 'prenom', 'telephone', 'email')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)

def _liberer_livreurs_queryset(queryset):
    """Remet à LIBRE les livreurs assignés aux demandes du queryset."""
    from Livreur.models import Livreur
    user_ids = queryset.exclude(coursier=None).values_list('coursier_id', flat=True)
    if user_ids:
        Livreur.objects.filter(user_id__in=user_ids).exclude(is_available='LIBRE').update(is_available='LIBRE')


@admin.action(description="Marquer sélectionnées comme Annulées")
def mark_as_cancelled(modeladmin, request, queryset):
    _liberer_livreurs_queryset(queryset)
    queryset.update(statut='ANNULEE')
    modeladmin.message_user(request, f"{queryset.count()} demande(s) marquée(s) comme annulée(s)")


@admin.action(description="Marquer sélectionnées comme Terminées")
def mark_as_completed(modeladmin, request, queryset):
    _liberer_livreurs_queryset(queryset)
    queryset.update(statut='TERMINEE')
    modeladmin.message_user(request, f"{queryset.count()} demande(s) marquée(s) comme terminée(s)")


class DCLAdmin(admin.ModelAdmin):
    list_display = (
        'ref', 'get_client_display', 'adresse_depart', 'adresse_destination',
        'type_course', 'cout_livraison', 'distance', 'statut', 'coursier', 'date_demande', 'date_recuperation', 'preview_photo'
    )
    list_filter = ('type_course', 'statut', 'date_demande', 'coursier')
    search_fields = ('ref', 'client__username', 'client_invite__nom', 'client_invite__prenom', 'client_invite__telephone', 'adresse_depart', 'adresse_destination')
    readonly_fields = ('date_demande', 'ref', 'preview_photo')
    date_hierarchy = 'date_demande'
    ordering = ('-date_demande',)
    actions = (mark_as_cancelled, mark_as_completed)

    fieldsets = (
        (None, {
            'fields': ('ref', 'client', 'client_invite', 'coursier', 'statut')
        }),
        ('Lieux', {
            'fields': (
                ('adresse_depart', 'adresse_destination'),
                ('latitude_depart', 'longitude_depart'),
                ('latitude_destination', 'longitude_destination'),
                'Contact_destinateur'
            )
        }),
        ('Colis', {
            'fields': ('description_colis', 'unite_poids', 'poids_colis', 'valeur_colis', 'photo_colis1', 'photo_colis2', 'preview_photo')
        }),
        ('Logistique', {
            'fields': ('type_course', 'distance', 'cout_livraison', 'date_recuperation', 'instructions')
        }),
    )

    def preview_photo(self, obj):
        """Affiche une miniature de la première photo si présente."""
        if obj.photo_colis1:
            return format_html('<img src="{}" style="max-height: 120px; max-width: 160px; object-fit: contain;"/>', obj.photo_colis1.url)
        return "Aucune"
    preview_photo.short_description = 'Aperçu photo'

    def get_client_display(self, obj):
        return obj.get_client_display()
    get_client_display.short_description = 'Client'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('client', 'client_invite', 'coursier')

    def save_model(self, request, obj, form, change):
        """Remplir la référence si besoin et journaliser la modification si nécessaire."""
        if not obj.ref:
            # Préfixe DCL pour une demande libre (invité, sans compte client), DC sinon
            prefix = 'DCL' if obj.client_id is None else 'DC'
            obj.ref = f'{prefix}-{uuid.uuid4().hex[:8].upper()}'
        super().save_model(request, obj, form, change)


admin.site.register(DCL, DCLAdmin)
