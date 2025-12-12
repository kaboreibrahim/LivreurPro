from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from Demande.models import DCL
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def commande_history(request):
    # Récupérer uniquement les commandes terminées ou annulées du client connecté
    commandes = DCL.objects.filter(
        client=request.user,
        statut__in=['TERMINEE', 'ANNULEE']
    ).order_by('-date_demande')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(commandes, 10)  # 10 commandes par page
    
    try:
        commandes_paginated = paginator.page(page)
    except PageNotAnInteger:
        commandes_paginated = paginator.page(1)
    except EmptyPage:
        commandes_paginated = paginator.page(paginator.num_pages)
    
    context = {
        'commandes': commandes_paginated,
        'page_title': 'Historique des commandes',
    }
    
    return render(request, 'Client/history/commande_history.html', context)

@login_required
def commande_detail(request, ref):
    # Récupérer les détails d'une commande spécifique
    commande = get_object_or_404(
        DCL,
        ref=ref,
        client=request.user,
        statut__in=['TERMINEE', 'ANNULEE']
    )
    
    context = {
        'commande': commande,
        'page_title': f'Détails de la commande {ref}',
    }
    
    return render(request, 'Client/history/commande_detail.html', context)