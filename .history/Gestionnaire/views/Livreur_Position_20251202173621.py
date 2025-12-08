
from Livreur.models import Livreur
from django.http import JsonResponse
 
### recupere les positions des livreurs 
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


#######liste des livreurs#########

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