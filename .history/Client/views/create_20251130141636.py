from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Demande.models import DCL
from Client.forms import DCLForm
from django.conf import settings

@login_required
def creer_demande_livraison(request):
    """Vue pour créer une nouvelle demande de livraison"""
    
    if request.method == 'POST':
        form = DCLForm(request.POST, request.FILES)
        
        if form.is_valid():
            demande = form.save(commit=False)
            demande.client = request.user
            demande.save()
            
            messages.success(
                request, 
                f'Votre demande {demande.ref} a été créée avec succès !'
            )
            return redirect('Client:detail_demande', pk=demande.id)
        else:
            messages.error(
                request, 
                'Erreur lors de la création de la demande. Veuillez vérifier les champs.'
            )
    else:
        form = DCLForm()
    
    context = {
        'form': form,
        'mapbox_token': settings.MAPBOX_ACCESS_TOKEN,
    }
    
    return render(request, 'livraison/create.html', context)