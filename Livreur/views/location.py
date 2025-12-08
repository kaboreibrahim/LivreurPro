from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from ..models import Livreur

@login_required
@require_http_methods(["GET"])
@csrf_exempt  # À remplacer par un token CSRF approprié en production
def update_livreur_location(request):
    user = request.user
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    
    if not all([latitude, longitude]):
        return JsonResponse(
            {'status': 'error', 'message': 'Latitude et longitude requises'}, 
            status=400
        )
    
    try:
        livreur = Livreur.objects.get(user=user)
        livreur.latitude = float(latitude)
        livreur.longitude = float(longitude)
        livreur.save()
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Position mise à jour avec succès',
            'timestamp': timezone.now().isoformat()
        })
    except Livreur.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Livreur non trouvé'}, 
            status=404
        )
    except ValueError:
        return JsonResponse(
            {'status': 'error', 'message': 'Coordonnées GPS invalides'}, 
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': str(e)}, 
            status=500
        )
