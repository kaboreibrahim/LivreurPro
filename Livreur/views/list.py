from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
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
            
        # Récupérer l'utilisateur associé au livreur
        livreur_user = user.livreur.user
            
        # Récupérer le filtre de type de demande (classique/express)
        type_course = self.request.GET.get('type_course', '')
        # Récupérer le filtre d'état
        statut = self.request.GET.get('statut', '')
        # Récupérer le terme de recherche
        search_query = self.request.GET.get('search', '')
        
        # Filtrer les demandes assignées au livreur et exclure les demandes terminées
        queryset = DCL.objects.filter(coursier=livreur_user).exclude(statut='TERMINEE')
        
        # Appliquer les filtres
        if type_course:
            queryset = queryset.filter(type_course=type_course)
            
        if statut:
            queryset = queryset.filter(statut=statut)
            
        if search_query:
            queryset = queryset.filter(
                Q(adresse_depart__icontains=search_query) |
                Q(adresse_destination__icontains=search_query) |
                Q(client__username__icontains=search_query) |
                Q(id__icontains=search_query)
            )
            
        # Trier par date de création décroissante
        return queryset.order_by('-type_course')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ajouter les filtres actuels au contexte
        context['type_course'] = self.request.GET.get('type_course', '')
        context['statut'] = self.request.GET.get('statut', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Options pour les menus déroulants
        context['type_course'] = DCL.TYPE_COURSE_CHOICES
        context['statuts_demande'] = DCL.STATUT_CHOICES
        
        # Statistiques — 1 seule requête
        if hasattr(self.request.user, 'livreur'):
            livreur_user = self.request.user.livreur.user
            stats = DCL.objects.filter(coursier=livreur_user).aggregate(
                total_demandes=Count('id', filter=Q(statut='VALIDATION_LIVREUR')),
                demandes_en_cours=Count('id', filter=Q(statut__in=['LIVRAISON_EN_ROUTE', 'RECEPTION_COLIS', 'LIVREUR_ROUTE'])),
                demandes_terminees=Count('id', filter=Q(statut='TERMINEE')),
            )
            context.update(stats)
        
        return context