from django.utils import timezone  # Ajout de l'import correct
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from LivreurV1.models import CustomUser,Livreur
from django.db.models.signals import pre_save
from django.dispatch import receiver
def index_livreur(request, *args, **kwargs):
    if request.user.is_authenticated:
        messages.add_message(
            request, 
            messages.SUCCESS, 
            f"Bienvenue, {request.user.first_name} {request.user.last_name} (Livreur) !"
        )
        
        # if request.method == 'POST':
        #     try:
        #         data = json.loads(request.body)
        #         latitude = data.get('latitude')
        #         longitude = data.get('longitude')
                
        #         print(f"Latitude: {latitude}, Longitude: {longitude}")
                
        #         # Récupérer le livreur existant et mettre à jour ses coordonnées
        #         livreur = Livreur.objects.get(user=request.user)
        #         livreur.latitude = latitude
        #         livreur.longitude = longitude
        #         livreur.date_mise_a_jour_coordonnees = timezone.now()
        #         livreur.save()
                
        #         return JsonResponse({
        #             'status': 'success',
        #             'message': 'Position mise à jour avec succès'
        #         })
                
        #     except Livreur.DoesNotExist:
        #         return JsonResponse({
        #             'status': 'error',
        #             'message': 'Livreur non trouvé'
        #         }, status=404)
                
        #     except json.JSONDecodeError:
        #         return JsonResponse({
        #             'status': 'error',
        #             'message': 'Données JSON invalides'
        #         }, status=400)
                
        #     except Exception as e:
        #         print(f"Erreur: {str(e)}")
        #         return JsonResponse({
        #             'status': 'error',
        #             'message': 'Erreur lors de la mise à jour'
        #         }, status=500)
    
    return render(request, 'index_livreur.html', {'page_name': 'Accueil Livreur'})
 

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now

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

# def index_livreur(request, *args, **kwargs):
#     if request.user.is_authenticated:
#         messages.add_message(
#             request, messages.SUCCESS, f"Bienvenue, {request.user.first_name} {request.user.last_name} (Livreur) !"
#         )
    
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         latitude = data.get('latitude')
#         longitude = data.get('longitude')
#         print(f"Latitude: {latitude}, Longitude: {longitude}")
        
#         user=request.user
#         print (user)

#         # Utilisez `request.user` pour associer un utilisateur authentifié
#         latitude=latitude,
#         longitude=longitude
    
        
#     return render(request, 'index_livreur.html', {'page_name': 'Accueil Livreur'})



# from django.http import JsonResponse
# import json

# def save_location(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         latitude = data.get('latitude')
#         longitude = data.get('longitude')

#         # Ici, tu peux sauvegarder les données dans ta base ou effectuer un traitement
#         print(f"Latitude: {latitude}, Longitude: {longitude}")

#         return JsonResponse({'message': 'Localisation sauvegardée avec succès.'})
#     return JsonResponse({'error': 'Requête non autorisée.'}, status=400)
