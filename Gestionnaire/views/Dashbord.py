from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from Demande.models import DCL
from Livreur.models import Livreur

User = get_user_model()

EN_COURS_STATUTS = ['VALIDATION_CLIENT', 'VALIDATION_LIVREUR', 'LIVREUR_ROUTE', 'RECEPTION_COLIS', 'LIVRAISON_EN_ROUTE']


@login_required
def DashbordGestionnaire(request):
    now = timezone.now()
    today = now.date()
    first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # ── KPI globaux — 1 seule requête avec agrégation ────────────────────────
    kpi = DCL.objects.aggregate(
        total_demandes=Count('id'),
        en_attente=Count('id', filter=Q(statut='EN_ATTENTE')),
        en_cours=Count('id', filter=Q(statut__in=EN_COURS_STATUTS)),
        terminees=Count('id', filter=Q(statut='TERMINEE')),
        annulees=Count('id', filter=Q(statut='ANNULEE')),
        publiques=Count('id', filter=Q(client__isnull=True)),
        revenus_total=Sum('cout_livraison', filter=Q(statut='TERMINEE')),
        revenus_mois=Sum('cout_livraison', filter=Q(statut='TERMINEE', date_demande__gte=first_of_month)),
    )
    total_demandes = kpi['total_demandes']
    en_attente     = kpi['en_attente']
    en_cours       = kpi['en_cours']
    terminees      = kpi['terminees']
    annulees       = kpi['annulees']
    publiques      = kpi['publiques']
    revenus_total  = kpi['revenus_total'] or 0
    revenus_mois   = kpi['revenus_mois'] or 0

    # ── Livreurs — 1 seule requête ───────────────────────────────────────────
    livreur_kpi = Livreur.objects.aggregate(
        total_livreurs=Count('id'),
        livreurs_libres=Count('id', filter=Q(is_available='LIBRE')),
        livreurs_occupes=Count('id', filter=Q(is_available='OCCUPER')),
    )
    total_livreurs   = livreur_kpi['total_livreurs']
    livreurs_libres  = livreur_kpi['livreurs_libres']
    livreurs_occupes = livreur_kpi['livreurs_occupes']

    # ── Clients ──────────────────────────────────────────────────────────────
    total_clients = User.objects.filter(role='client').count()

    # ── Dernières demandes (10) ───────────────────────────────────────────────
    dernieres_demandes = (
        DCL.objects
        .select_related('client', 'client_invite', 'coursier')
        .order_by('-date_demande')[:10]
    )

    # ── Graphique 7 jours — 1 seule requête avec annotation ─────────────────
    seven_days_ago = today - timedelta(days=6)
    counts_par_jour = {
        row['jour']: row['nb']
        for row in DCL.objects
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

    # ── Donut : répartition par statut ───────────────────────────────────────
    statut_labels = ['En attente', 'En cours', 'Terminées', 'Annulées']
    statut_values = [en_attente, en_cours, terminees, annulees]
    statut_colors = ['#f59e0b', '#3b82f6', '#10b981', '#ef4444']

    context = {
        'now': now,
        'total_demandes':   total_demandes,
        'en_attente':       en_attente,
        'en_cours':         en_cours,
        'terminees':        terminees,
        'annulees':         annulees,
        'publiques':        publiques,
        'total_livreurs':   total_livreurs,
        'livreurs_libres':  livreurs_libres,
        'livreurs_occupes': livreurs_occupes,
        'total_clients':    total_clients,
        'revenus_mois':     revenus_mois,
        'revenus_total':    revenus_total,
        'dernieres_demandes': dernieres_demandes,
        'chart_labels':   json.dumps(chart_labels),
        'chart_data':     json.dumps(chart_data),
        'statut_labels':  json.dumps(statut_labels),
        'statut_values':  json.dumps(statut_values),
        'statut_colors':  json.dumps(statut_colors),
    }

    return render(request, 'pages/dashbord_gestionnaire.html', context)
