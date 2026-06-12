from django.views.generic import DetailView
from django.conf import settings
import json

from Demande.models import DCL
from Livreur.models import Livreur


# Ordered success path (linear flow, ANNULEE excluded)
STATUT_SUCCESS_PATH = [
    'EN_ATTENTE',
    'VALIDATION_CLIENT',
    'VALIDATION_LIVREUR',
    'LIVREUR_ROUTE',
    'RECEPTION_COLIS',
    'LIVRAISON_EN_ROUTE',
    'TERMINEE',
]

STATUT_ICONS = {
    'EN_ATTENTE':         'bi-clock-history',
    'VALIDATION_CLIENT':  'bi-currency-dollar',
    'VALIDATION_LIVREUR': 'bi-person-check',
    'LIVREUR_ROUTE':      'bi-bicycle',
    'RECEPTION_COLIS':    'bi-box-seam',
    'LIVRAISON_EN_ROUTE': 'bi-truck',
    'TERMINEE':           'bi-check-circle-fill',
    'ANNULEE':            'bi-x-circle-fill',
}


class DetailDemandeView(DetailView):
    model = DCL
    template_name = 'Gestionnaire/pages/detail_demande.html'
    context_object_name = 'demande'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        demande = self.object

        # Livreurs disponibles (pour modal assignation)
        context['livreurs_disponibles'] = (
            Livreur.objects.filter(is_available='LIBRE').select_related('user')
        )

        # Mapbox token
        context['mapbox_token'] = getattr(settings, 'MAPBOX_ACCESS_TOKEN', '')

        # Coordonnées JSON (float Python → toujours avec point, peu importe la locale)
        has_coords = all([
            demande.latitude_depart, demande.longitude_depart,
            demande.latitude_destination, demande.longitude_destination,
        ])
        if has_coords:
            context['map_data'] = json.dumps({
                'token': getattr(settings, 'MAPBOX_ACCESS_TOKEN', ''),
                'dep':   [float(demande.longitude_depart),   float(demande.latitude_depart)],
                'dest':  [float(demande.longitude_destination), float(demande.latitude_destination)],
                'dep_addr':  demande.adresse_depart,
                'dest_addr': demande.adresse_destination,
            })
        else:
            context['map_data'] = None

        # Statut choices (for modals / dropdowns)
        context['statut_choices'] = DCL.STATUT_CHOICES

        # Timeline: success path with index
        success_path = []
        current_idx = -1
        for i, key in enumerate(STATUT_SUCCESS_PATH):
            label = dict(DCL.STATUT_CHOICES).get(key, key)
            icon  = STATUT_ICONS.get(key, 'bi-circle')
            is_current   = (demande.statut == key)
            is_completed = False
            is_pending   = True
            if demande.statut in STATUT_SUCCESS_PATH:
                ci = STATUT_SUCCESS_PATH.index(demande.statut)
                is_completed = i < ci
                is_current   = i == ci
                is_pending   = i > ci
                if is_current:
                    current_idx = i
            success_path.append({
                'key':          key,
                'label':        label,
                'icon':         icon,
                'is_current':   is_current,
                'is_completed': is_completed,
                'is_pending':   is_pending,
            })

        context['success_path']     = success_path
        context['current_status_index'] = current_idx
        context['is_cancelled']     = (demande.statut == 'ANNULEE')

        return context
