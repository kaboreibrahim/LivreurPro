from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from Demande.models import DCL
from Livreur.models import Livreur
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Case, When, IntegerField, Q

from 
class ListeDemandesView(ListView):
    model = DCL
    template_name = 'Gestionnaire/pages/liste_demandes.html'
    context_object_name = 'demandes'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = DCL.objects.all().order_by('-date_demande')
        
        # Filtre par statut 
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
            
        # Filtre par type de course
        type_course = self.request.GET.get('type_course')
        if type_course:
            queryset = queryset.filter(type_course=type_course)
            
        # Recherche par référence, adresse ou client
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(ref__icontains=search_query) |
                Q(adresse_depart__icontains=search_query) |
                Q(adresse_destination__icontains=search_query) |
                Q(client__username__icontains=search_query) |
                Q(Contact_destinateur__icontains=search_query)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer les paramètres de filtrage pour les garder dans le formulaire
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_statut'] = self.request.GET.get('statut', '')
        context['selected_type'] = self.request.GET.get('type_course', '')
        
        # Options pour les filtres
        context['statut_choices'] = DCL.STATUT_CHOICES
        context['type_course_choices'] = DCL.TYPE_COURSE_CHOICES
        
        # Statistiques pour le tableau de bord
        context['total_demandes'] = DCL.objects.count()
        context['demandes_en_attente'] = DCL.objects.filter(statut='EN_ATTENTE').count()
        context['demandes_en_cours'] = DCL.objects.filter(
            statut__in=['VALIDATION_CLIENT', 'VALIDATION_LIVREUR', 'LIVREUR_ROUTE', 'RECEPTION_COLIS', 'LIVRAISON_EN_ROUTE']
        ).count()
        context['demandes_terminees'] = DCL.objects.filter(statut='TERMINEE').count()
        
        return context

class DetailDemandeView(DetailView):
    model = DCL
    template_name = 'Gestionnaire/pages/detail_demande.html'
    context_object_name = 'demande'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Vous pouvez ajouter ici des données supplémentaires si nécessaire
        return context

def changer_statut(request, pk, nouveau_statut):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission d'effectuer cette action.")
        return redirect('gestionnaire:liste_demandes')
        
    demande = get_object_or_404(DCL, pk=pk)
    ancien_statut = demande.get_statut_display()
    demande.statut = nouveau_statut
    
    # Mettre à jour la date de mise à jour si nécessaire
    if nouveau_statut == 'TERMINEE':
        demande.date_livraison = timezone.now()
    
    demande.save()
    
    messages.success(
        request, 
        f"Le statut de la demande {demande.ref} a été modifié de '{ancien_statut}' à '{demande.get_statut_display()}'"
    )
    
    return redirect('gestionnaire:detail_demande', pk=demande.pk)

def modifier_prix(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission d'effectuer cette action.")
        return redirect('Gestionnaire:liste_demandes')
    
    if request.method == 'POST':
        demande = get_object_or_404(DCL, pk=pk)
        nouveau_prix = request.POST.get('prix')
        nouveau_statut = request.POST.get('nouveau_statut')
        
        if not nouveau_prix:
            messages.error(request, "Veuillez saisir un prix valide.")
            return redirect('Gestionnaire:detail_demande', pk=demande.pk)
        
        try:
            # Mettre à jour le prix
            demande.cout_livraison = float(nouveau_prix)
            
            # Mettre à jour le statut si fourni
            if nouveau_statut:
                ancien_statut = demande.get_statut_display()
                demande.statut = nouveau_statut
                demande.save()
                
                messages.success(
                    request,
                    f"Le prix de la livraison a été défini à {demande.cout_livraison} FCFA. "
                    f"Le statut est maintenant : {demande.get_statut_display()}"
                )
            else:
                demande.save()
                messages.success(request, f"Le prix de la livraison a été mis à jour à {demande.cout_livraison} FCFA.")
                
        except (ValueError, TypeError):
            messages.error(request, "Le prix saisi n'est pas valide.")
        
        return redirect('Gestionnaire:detail_demande', pk=demande.pk)
    
    return redirect('Gestionnaire:liste_demandes')


@login_required
def get_livreur_positions(request):
    livreurs = Livreur.objects.filter(latitude__isnull=False, longitude__isnull=False)
    data = [
        {
            'username': livreur.user.username,
            'latitude': float(livreur.latitude),
            'longitude': float(livreur.longitude),
            'is_available': livreur.is_available,
            'adresse': livreur.adresse,
            "photo": livreur.user.photos.url
        }
        for livreur in livreurs
    ]
    return JsonResponse(data, safe=False)

@method_decorator(login_required, name='dispatch')
class LivreurDisponible(ListView):
    model = Livreur
    template_name = 'pages/livreur_disponible.html'
    context_object_name = 'livreur_disponible'

    def get_queryset(self):
        return Livreur.objects.annotate(
            type_order=Case(
                When(is_available='LIBRE', then=0),
                When(is_available='OCCUPER', then=1),
                output_field=IntegerField(),
            )
        ).order_by('type_order')