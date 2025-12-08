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




@csrf_exempt  # Si vous utilisez GET, Django n'exige pas le CSRF, mais vérifiez vos règles de sécurité
def save_location(request):
    if request.method == "GET":
        # Récupérer les coordonnées depuis les paramètres de la requête GET
        latitude = request.GET.get('latitude')
        print(latitude)
        longitude = request.GET.get('longitude')
        print(longitude)

        if latitude and longitude:
            # Récupérer le livreur existant et mettre à jour ses coordonnées
            livreur = Livreur.objects.get(user=request.user)
            livreur.latitude = latitude
            livreur.longitude = longitude
            livreur.date_mise_a_jour_coordonnees = timezone.now()
            livreur.save()
            return JsonResponse({
                "message": "Localisation sauvegardée avec succès.",
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": now()
            }, status=200)
        else:
            return JsonResponse({"error": "Latitude et longitude sont obligatoires."}, status=400)

    return JsonResponse({"error": "Méthode non autorisée."}, status=405)


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