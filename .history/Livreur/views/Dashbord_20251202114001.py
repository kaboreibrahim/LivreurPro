from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from Livreur.models import Livreur

@login_required
def DashbordLivreur(request, *args, **kwargs):
    
    return render(request, 'pages/dashbord_livreur.html')



# @login_required
# def get_livreur_positions(request):
#     livreurs = Livreur.objects.filter(latitude__isnull=False, longitude__isnull=False)
#     data = [
#         {
#             'username': livreur.user.username,
#             'latitude': float(livreur.latitude),
#             'longitude': float(livreur.longitude),
#             'is_available': livreur.is_available,
#             'adresse': livreur.adresse,
#             "photo": livreur.user.photos.url
#         }
#         for livreur in livreurs
#     ]
#     return JsonResponse(data, safe=False)