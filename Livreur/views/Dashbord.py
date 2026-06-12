from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, Count, Q
from datetime import timedelta
import json

from Livreur.models import Livreur
from Demande.models import DCL


@login_required
def DashbordLivreur(request, *args, **kwargs):
    user = request.user
    livreur = getattr(user, 'livreur', None)

    if livreur:
        base_qs = DCL.objects.filter(coursier=user)
        debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # ── Stats de base — 1 seule requête ────────────────────────────────
        stats = base_qs.aggregate(
            a_accepter=Count('id', filter=Q(statut='VALIDATION_LIVREUR')),
            en_cours=Count('id', filter=Q(statut__in=['LIVREUR_ROUTE', 'RECEPTION_COLIS', 'LIVRAISON_EN_ROUTE'])),
            terminees_total=Count('id', filter=Q(statut='TERMINEE')),
            terminees_mois=Count('id', filter=Q(statut='TERMINEE', date_livraison__gte=debut_mois)),
            revenus_mois=Sum('cout_livraison', filter=Q(statut='TERMINEE', date_livraison__gte=debut_mois)),
        )
        a_accepter      = stats['a_accepter']
        en_cours        = stats['en_cours']
        terminees_total = stats['terminees_total']
        terminees_mois  = stats['terminees_mois']
        revenus_mois    = stats['revenus_mois'] or 0

        # ── 5 dernières courses ────────────────────────────────────────────
        dernieres_courses = base_qs.order_by('-date_demande')[:5]

        # ── Graphique 7 jours — 1 seule requête ───────────────────────────
        today = timezone.localdate()
        seven_days_ago = today - timedelta(days=6)
        counts_par_jour = {
            row['jour']: row['nb']
            for row in base_qs
            .filter(date_demande__date__gte=seven_days_ago)
            .extra(select={'jour': "DATE(date_demande)"})
            .values('jour')
            .annotate(nb=Count('id'))
        }
        chart_labels, chart_data = [], []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            chart_labels.append(day.strftime('%d/%m'))
            chart_data.append(counts_par_jour.get(day, 0))
    else:
        a_accepter = en_cours = terminees_total = terminees_mois = 0
        revenus_mois = 0
        dernieres_courses = DCL.objects.none()
        today = timezone.localdate()
        chart_labels = [(today - timedelta(days=i)).strftime('%d/%m') for i in range(6, -1, -1)]
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
