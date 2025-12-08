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
    template_name = 'Gestionnaire/client/list.html'
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
    template_name = 'Gestionnaire/client/detail.html'
    context_object_name = 'client'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return CustomUser.objects.filter(role='client')

def activer_desactiver_client(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission d'effectuer cette action.")
        return redirect('gestionnaire:liste_clients')
        
    client = get_object_or_404(CustomUser, pk=pk, role='client')
    client.is_active = not client.is_active
    client.save()
    
    status = "activé" if client.is_active else "désactivé"
    messages.success(
        request,
        f"Le compte client {client.username} a été {status} avec succès."
    )
    
    return redirect('gestionnaire:liste_clients')