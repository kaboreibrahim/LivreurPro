from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from Auth.models import CustomUser

@method_decorator(login_required, name='dispatch')
class ListeClientsView(ListView):
    model = CustomUser
    template_name = 'client/list.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        queryset = CustomUser.objects.filter(role='client').order_by('-date_joined')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
            
        # Search by username, email, or contact
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(Contact__icontains=search_query)
            )
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


@method_decorator(login_required, name='dispatch')
class DetailClientView(DetailView):
    model = CustomUser
    template_name = 'client/detail.html'
    context_object_name = 'client'
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        return CustomUser.objects.filter(role='client')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.object
        
        # Récupérer toutes les demandes du client
        demandes = DCL.objects.filter(client=client).order_by('-date_demande')
        
        # Statistiques des demandes
        demandes_stats = demandes.aggregate(
            total_demandes=Count('id'),
            demandes_en_attente=Count('id', filter=Q(statut='EN_ATTENTE')),
            demandes_en_cours=Count('id', filter=Q(
                statut__in=['VALIDATION_CLIENT', 'VALIDATION_LIVREUR', 'LIVREUR_ROUTE', 
                           'RECEPTION_COLIS', 'LIVRAISON_EN_ROUTE']
            )),
            demandes_terminees=Count('id', filter=Q(statut='TERMINEE')),
            demandes_annulees=Count('id', filter=Q(statut='ANNULEE')),
            montant_total=Sum('cout_livraison'),
        )
        
        # Convertir None en 0 pour montant_total
        if demandes_stats['montant_total'] is None:
            demandes_stats['montant_total'] = Decimal('0.00')
        
        # Statistiques par type de course
        demandes_expresses = demandes.filter(type_course='EXPRESSE').count()
        demandes_classiques = demandes.filter(type_course='CLASSIQUE').count()
        
        context['demandes'] = demandes
        context['demandes_stats'] = demandes_stats
        context['demandes_expresses'] = demandes_expresses
        context['demandes_classiques'] = demandes_classiques
        
        # Pour la recherche (si vous avez une fonctionnalité de recherche)
        context['search_query'] = self.request.GET.get('q', '')
        
        return context

def activer_desactiver_client(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission d'effectuer cette action.")
        return redirect('Gestionnaire:liste_clients')
        
    client = get_object_or_404(CustomUser, pk=pk, role='client')
    client.is_active = not client.is_active
    client.save()
    
    status = "activé" if client.is_active else "désactivé"
    messages.success(
        request,
        f"Le compte client {client.username} a été {status} avec succès."
    )
    
    return redirect('Gestionnaire:liste_clients')