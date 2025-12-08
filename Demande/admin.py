from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import DCL
import uuid

@admin.action(description="Marquer sélectionnées comme Annulées")
def mark_as_cancelled(modeladmin, request, queryset):
    queryset.update(statut='ANNULEE')
    modeladmin.message_user(request, f"{queryset.count()} demande(s) marquée(s) comme annulée(s)")


@admin.action(description="Marquer sélectionnées comme Terminées")
def mark_as_completed(modeladmin, request, queryset):
    queryset.update(statut='TERMINEE')
    modeladmin.message_user(request, f"{queryset.count()} demande(s) marquée(s) comme terminée(s)")


class DCLAdmin(admin.ModelAdmin):
    list_display = (
        'ref', 'client', 'adresse_depart', 'adresse_destination',
        'type_course', 'cout_livraison', 'distance', 'statut', 'coursier', 'date_demande', 'date_recuperation', 'preview_photo'
    )
    list_filter = ('type_course', 'statut', 'date_demande', 'coursier')
    search_fields = ('ref', 'client__username', 'adresse_depart', 'adresse_destination')
    readonly_fields = ('date_demande', 'ref', 'preview_photo')
    date_hierarchy = 'date_demande'
    ordering = ('-date_demande',)
    actions = (mark_as_cancelled, mark_as_completed)

    fieldsets = (
        (None, {
            'fields': ('ref', 'client', 'coursier', 'statut')
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
            'fields': ('description_colis', 'poids_colis', 'valeur_colis', 'photo_colis1', 'photo_colis2', 'preview_photo')
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

    def get_queryset(self, request):
        """Optimise les requêtes si nécessaire."""
        qs = super().get_queryset(request)
        return qs.select_related('client', 'coursier')

    def save_model(self, request, obj, form, change):
        """Remplir la référence si besoin et journaliser la modification si nécessaire."""
        if not obj.ref:
            obj.ref = f'DCL-{uuid.uuid4().hex[:8].upper()}'
        super().save_model(request, obj, form, change)


admin.site.register(DCL, DCLAdmin)
