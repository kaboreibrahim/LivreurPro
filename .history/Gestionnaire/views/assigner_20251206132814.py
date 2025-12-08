from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from Livreur.models import Livreur
from Demande.models import DCL

@require_http_methods(["GET"])
def assigner_livreur_modal(request, demande_id):
    """Affiche le modal d'assignation de livreur"""
    # Récupérer les livreurs disponibles
    livreurs_disponibles = Livreur.objects.filter(is_available='LIBRE')
    print(livreurs_disponibles)
    context = {
        'livreurs_disponibles': livreurs_disponibles,
        'demande_id': demande_id
    }
    return render(request, 'Gestionnaire/modals/assigner_livreur_modal.html', context)

@require_http_methods(["POST"])
def assigner_livreur(request, demande_id):
    """Traite l'assignation d'un livreur à une demande"""
    # Récupérer la demande et le livreur
    demande = get_object_or_404(DCL, id=demande_id)
    livreur_id = request.POST.get('livreur_id')
    
    if not livreur_id:
        return JsonResponse({'success': False, 'message': 'Veuillez sélectionner un livreur'})
    
    try:
        livreur = Livreur.objects.get(id=livreur_id, is_available='LIBRE')
        
        # Mettre à jour la demande
        demande.coursier = livreur.user
        demande.statut = 'VALIDATION_LIVREUR'  # Statut en attente de validation du livreur
        demande.save()
        
        # Mettre à jour le statut du livreur
        livreur.is_available = 'OCCUPER'
        livreur.save()
        
        messages.success(request, f'La demande a été assignée à {livreur.user.get_full_name() or livreur.user.username}')
        return JsonResponse({
            'success': True,
            'message': 'Livreur assigné avec succès',
            'livreur_nom': f"{livreur.user.get_full_name() or livreur.user.username}",
            'statut': 'En attente de validation du livreur'
        })
        
    except Livreur.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Livreur non trouvé ou non disponible'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Une erreur est survenue: {str(e)}'})