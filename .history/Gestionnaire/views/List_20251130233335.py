from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from Demande.models import DCL
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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

    