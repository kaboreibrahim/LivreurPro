from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from Demande.models import DCL
 

def modifier_prix(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission d'effectuer cette action.")
        return redirect('Gestionnaire:liste_demandes')
    
    if request.method == 'POST':
        demande = get_object_or_404(DCL, pk=pk)
        nouveau_prix = request.POST.get('prix')
        nouveau_statut = request.POST.get('nouveau_statut')
        
        if not nouveau_prix:
            messages.error(request, "Veuillez saisir un prix valide.")
            return redirect('Gestionnaire:detail_demande', pk=demande.pk)
        
        try:
            # Mettre à jour le prix
            demande.cout_livraison = float(nouveau_prix)
            
            # Mettre à jour le statut si fourni
            if nouveau_statut:
                ancien_statut = demande.get_statut_display()
                demande.statut = nouveau_statut
                demande.save()
                
                messages.success(
                    request,
                    f"Le prix de la livraison a été défini à {demande.cout_livraison} FCFA. "
                    f"Le statut est maintenant : {demande.get_statut_display()}"
                )
            else:
                demande.save()
                messages.success(request, f"Le prix de la livraison a été mis à jour à {demande.cout_livraison} FCFA.")
                
        except (ValueError, TypeError):
            messages.error(request, "Le prix saisi n'est pas valide.")
        
        return redirect('Gestionnaire:detail_demande', pk=demande.pk)
    
    return redirect('Gestionnaire:liste_demandes')
