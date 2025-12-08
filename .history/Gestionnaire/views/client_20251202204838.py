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
        queryset = CustomUser.objects.filter(role='client')
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(telephone__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.get_object()
        
        # Importer les modèles nécessaires
        from django.db.models import Count, Sum, Q
        
        # Statistiques des commandes
        commandes_stats = {'total_commandes': 0, 'commandes_livrees': 0, 
                          'commandes_en_cours': 0, 'montant_total': 0}
        
        # Statistiques des colis
        colis_stats = {'total_colis': 0, 'colis_livres': 0, 
                       'colis_en_attente': 0, 'colis_en_cours': 0}
        
        # Vérifier si les modèles existent avant de faire les requêtes
        try:
            from commande.models import Commande
            commandes_stats = Commande.objects.filter(client=client).aggregate(
                total_commandes=Count('id'),
                commandes_livrees=Count('id', filter=Q(statut='livree')),
                commandes_en_cours=Count('id', filter=Q(statut='en_cours')),
                montant_total=Sum('montant_total') or 0
            )
        except ImportError:
            pass
            
        try:
            from colis.models import Colis
            colis_stats = Colis.objects.filter(commande__client=client).aggregate(
                total_colis=Count('id'),
                colis_livres=Count('id', filter=Q(statut='livre')),
                colis_en_attente=Count('id', filter=Q(statut='en_attente')),
                colis_en_cours=Count('id', filter=Q(statut='en_cours'))
            )
        except ImportError:
            pass
        
        context.update({
            'commandes_stats': commandes_stats,
            'colis_stats': colis_stats,
            'search_query': self.request.GET.get('q', ''),
        })
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