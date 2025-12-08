from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from Demande.models import DCL
from Livreur.models import Livreur
from django.utils import timezone

class DemandeLivreurListView(LoginRequiredMixin, ListView):
    model = DCL
    template_name = 'livreur/demande_liste.html'
    context_object_name = 'demandes'
    paginate_by = 10
    
    def get_queryset(self):
        # Récupérer l'utilisateur connecté
        user = self.request.user
        if not hasattr(user, 'livreur'):
            return DCL.objects.none()
            
        # Récupérer le filtre de type de demande (classique/express)
        type_demande = self.request.GET.get('type_demande', '')
        # Récupérer le filtre d'état
        etat = self.request.GET.get('etat', '')
        # Récupérer le terme de recherche
        search_query = self.request.GET.get('search', '')
        
        # Filtrer les demandes assignées au livreur
        queryset = DCL.objects.filter(coursier=user.livreur)
        
        # Appliquer les filtres
        if type_demande:
            queryset = queryset.filter(type_demande=type_demande)
            
        if etat:
            queryset = queryset.filter(etat=etat)
            
        if search_query:
            queryset = queryset.filter(
                Q(adresse_depart__icontains=search_query) |
                Q(adresse_destination__icontains=search_query) |
                Q(client__username__icontains=search_query) |
                Q(id__icontains=search_query)
            )
            
        # Trier par date de création décroissante
        return queryset.order_by('-date_creation')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ajouter les filtres actuels au contexte
        context['type_demande'] = self.request.GET.get('type_demande', '')
        context['etat'] = self.request.GET.get('etat', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Options pour les menus déroulants
        context['types_demande'] = DCL.TYPE_DEMANDE_CHOICES
        context['etats_demande'] = DCL.ETAT_CHOICES
        
        # Statistiques pour le tableau de bord
        if hasattr(self.request.user, 'livreur'):
            livreur = self.request.user.livreur
            context['total_demandes'] = DCL.objects.filter(coursier=livreur).count()
            context['demandes_en_cours'] = DCL.objects.filter(
                coursier=livreur,
                etat__in=['EN_COURS', 'EN_ATTENTE']
            ).count()
            context['demandes_terminees'] = DCL.objects.filter(
                coursier=livreur,
                etat='TERMINE'
            ).count()
        
        return context