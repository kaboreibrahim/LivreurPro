from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from django.db.models import Q, Count, Case, When, IntegerField
from django.contrib import messages
from django.utils import timezone


from django.contrib.auth import get_user_model
from django.db.models.functions import Concat
from django.db.models import Value as V
from django.contrib.auth.models import Group

User = get_user_model()

class ListeClientsView(ListView):
    model = User
    template_name = 'Gestionnaire/client/list.html'
    context_object_name = 'clients'
    paginate_by = 15
    
    def get_queryset(self):
        # Récupérer uniquement les utilisateurs du groupe 'client'
        client_group = Group.objects.get(name='client')
        queryset = User.objects.filter(groups=client_group).annotate(
            full_name=Concat('first_name', V(' '), 'last_name')
        ).order_by('-date_joined')
        
        # Filtre par statut (actif/inactif)
        is_active = self.request.GET.get('is_active')
        if is_active in ['true', 'false']:
            queryset = queryset.filter(is_active=(is_active == 'true'))
            
        # Recherche par nom, prénom, email ou téléphone
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(telephone__icontains=search_query)
            )
            
        # Trier par nombre de commandes
        sort_by = self.request.GET.get('sort_by')
        if sort_by == 'commandes':
            queryset = queryset.annotate(
                commandes_count=Count('client_demandes')
            ).order_by('-commandes_count')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer les paramètres de filtrage
        context['search_query'] = self.request.GET.get('q', '')
        context['is_active_filter'] = self.request.GET.get('is_active', '')
        
        # Statistiques clients
        client_group = Group.objects.get(name='client')
        total_clients = User.objects.filter(groups=client_group).count()
        clients_actifs = User.objects.filter(groups=client_group, is_active=True).count()
        
        context.update({
            'total_clients': total_clients,
            'clients_actifs': clients_actifs,
            'clients_inactifs': total_clients - clients_actifs,
            'clients_nouveaux': User.objects.filter(
                groups=client_group,
                date_joined__date=timezone.now().date()
            ).count(),
        })
        
        return context

def activer_desactiver_client(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission d'effectuer cette action.")
        return redirect('gestionnaire:liste_clients')
        
    client = get_object_or_404(User, pk=pk)
    client.is_active = not client.is_active
    client.save()
    
    action = "activé" if client.is_active else "désactivé"
    messages.success(
        request, 
        f"Le client {client.get_full_name()} a été {action} avec succès."
    )
    
    return redirect('gestionnaire:liste_clients')

