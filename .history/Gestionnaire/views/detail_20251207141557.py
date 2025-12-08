from django.views.generic import DetailView 
from Demande.models import DCL
from Livreur.models import Livreur
 
class DetailDemandeView(DetailView):
    model = DCL
    template_name = 'Gestionnaire/pages/detail_demande.html'
    context_object_name = 'demande'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter les livreurs disponibles au contexte
        context['livreurs_disponibles'] = Livreur.objects.filter(is_available='LIBRE').select_related('user')
        return context