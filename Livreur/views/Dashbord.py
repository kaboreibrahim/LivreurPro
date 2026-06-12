from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum
from datetime import timedelta
import json

from Livreur.models import Livreur
from Demande.models import DCL


@login_required
def DashbordLivreur(request, *args, **kwargs):
    user = request.user
    livreur = getattr(user, 'livreur', None)

    # ── Stats de base ──────────────────────────────────────────────────────────
    if livreur:
        base_qs = DCL.objects.filter(coursier=user)

        a_accepter = base_qs.filter(statut='VALIDATION_LIVREUR').count()
        en_cours = base_qs.filter(
            statut__in=['LIVREUR_ROUTE', 'RECEPTION_COLIS', 'LIVRAISON_EN_ROUTE']
        ).count()
        terminees_total = base_qs.filter(statut='TERMINEE').count()

        # Revenus du mois en cours
        debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        revenus_mois = (
            base_qs
            .filter(statut='TERMINEE', date_livraison__gte=debut_mois)
            .aggregate(total=Sum('cout_livraison'))['total'] or 0
        )
        terminees_mois = base_qs.filter(
            statut='TERMINEE', date_livraison__gte=debut_mois
        ).count()

        # ── 5 dernières courses ────────────────────────────────────────────────
        dernieres_courses = base_qs.order_by('-date_demande')[:5]

        # ── Graphique : évolution sur 7 jours ─────────────────────────────────
        today = timezone.localdate()
        chart_labels = []
        chart_data = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            chart_labels.append(day.strftime('%d/%m'))
            chart_data.append(
                base_qs.filter(date_demande__date=day).count()
            )
    else:
        a_accepter = en_cours = terminees_total = terminees_mois = 0
        revenus_mois = 0
        dernieres_courses = DCL.objects.none()
        chart_labels = [(timezone.localdate() - timedelta(days=i)).strftime('%d/%m') for i in range(6, -1, -1)]
        chart_data = [0] * 7

    context = {
        'livreur': livreur,
        'a_accepter': a_accepter,
        'en_cours': en_cours,
        'terminees_total': terminees_total,
        'terminees_mois': terminees_mois,
        'revenus_mois': revenus_mois,
        'dernieres_courses': dernieres_courses,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'now': timezone.now(),
        'mapbox_token': getattr(settings, 'MAPBOX_ACCESS_TOKEN', ''),
    }
    return render(request, 'pages/dashbord_livreur.html', context)
