from django.views.generic import DetailView 
from Demande.models import DCL
 
class DetailDemandeView(DetailView):
    model = DCL
    template_name = 'Gestionnaire/pages/detail_demande.html'
    context_object_name = 'demande'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Vous pouvez ajouter ici des données supplémentaires si nécessaire
        return context