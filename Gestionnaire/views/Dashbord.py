from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
import json

from Demande.models import DCL
from Livreur.models import Livreur

User = get_user_model()


@login_required
def DashbordGestionnaire(request):
    now = timezone.now()
    today = now.date()
    first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # ── KPI globaux ──────────────────────────────────────────────────────────
    total_demandes    = DCL.objects.count()
    en_attente        = DCL.objects.filter(statut='EN_ATTENTE').count()
    en_cours          = DCL.objects.filter(statut__in=[
        'VALIDATION_CLIENT', 'VALIDATION_LIVREUR',
        'LIVREUR_ROUTE', 'RECEPTION_COLIS', 'LIVRAISON_EN_ROUTE'
    ]).count()
    terminees         = DCL.objects.filter(statut='TERMINEE').count()
    annulees          = DCL.objects.filter(statut='ANNULEE').count()
    publiques         = DCL.objects.filter(client__isnull=True).count()

    # ── Livreurs ─────────────────────────────────────────────────────────────
    total_livreurs    = Livreur.objects.count()
    livreurs_libres   = Livreur.objects.filter(is_available='LIBRE').count()
    livreurs_occupes  = Livreur.objects.filter(is_available='OCCUPER').count()

    # ── Clients ──────────────────────────────────────────────────────────────
    total_clients     = User.objects.filter(role='client').count()

    # ── Revenus ──────────────────────────────────────────────────────────────
    revenus_mois = (
        DCL.objects.filter(statut='TERMINEE', date_demande__gte=first_of_month)
        .aggregate(total=Sum('cout_livraison'))['total'] or 0
    )
    revenus_total = (
        DCL.objects.filter(statut='TERMINEE')
        .aggregate(total=Sum('cout_livraison'))['total'] or 0
    )

    # ── Dernières demandes (10) ───────────────────────────────────────────────
    dernieres_demandes = (
        DCL.objects
        .select_related('client', 'client_invite', 'coursier')
        .order_by('-date_demande')[:10]
    )

    # ── Graphique : demandes par jour (7 derniers jours) ─────────────────────
    chart_labels, chart_data = [], []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        chart_labels.append(day.strftime('%d/%m'))
        chart_data.append(DCL.objects.filter(date_demande__date=day).count())

    # ── Donut : répartition par statut ───────────────────────────────────────
    statut_labels = ['En attente', 'En cours', 'Terminées', 'Annulées']
    statut_values = [en_attente, en_cours, terminees, annulees]
    statut_colors = ['#f59e0b', '#3b82f6', '#10b981', '#ef4444']

    context = {
        'now': now,
        # KPI
        'total_demandes':   total_demandes,
        'en_attente':       en_attente,
        'en_cours':         en_cours,
        'terminees':        terminees,
        'annulees':         annulees,
        'publiques':        publiques,
        # Livreurs
        'total_livreurs':   total_livreurs,
        'livreurs_libres':  livreurs_libres,
        'livreurs_occupes': livreurs_occupes,
        # Clients / revenus
        'total_clients':    total_clients,
        'revenus_mois':     revenus_mois,
        'revenus_total':    revenus_total,
        # Table
        'dernieres_demandes': dernieres_demandes,
        # Charts (JSON-safe)
        'chart_labels':   json.dumps(chart_labels),
        'chart_data':     json.dumps(chart_data),
        'statut_labels':  json.dumps(statut_labels),
        'statut_values':  json.dumps(statut_values),
        'statut_colors':  json.dumps(statut_colors),
    }

    return render(request, 'pages/dashbord_gestionnaire.html', context)
