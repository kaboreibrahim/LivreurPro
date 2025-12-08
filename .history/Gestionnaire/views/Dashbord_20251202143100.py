from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.http import JsonResponse
from Livreur.models import Livreur
from django.db.models import Case, When, IntegerField
@login_required
def DashbordGestionnaire(request, *args, **kwargs):
    
    return render(request, 'pages/dashbord_gestionnaire.html')


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


