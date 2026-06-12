from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.conf import settings

from Demande.forms import DCLPublicForm
from Demande.models import DCL


def demande_publique(request):
    """
    Formulaire de demande de coursier accessible sans connexion.
    Si l'utilisateur est déjà connecté en tant que client, on le redirige
    vers son espace dédié pour éviter toute confusion.
    """
    if request.user.is_authenticated and getattr(request.user, 'role', None) == 'client':
        return redirect('Client:creer_demande')

    if request.method == 'POST':
        form = DCLPublicForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    demande = form.save_as_guest()
                    demande.calculate_distance()
                messages.success(
                    request,
                    f'Votre demande {demande.ref} a été soumise avec succès ! '
                    'Nous vous contacterons très prochainement.'
                )
                return redirect('demande_confirmation', ref=demande.ref)
            except Exception as e:
                messages.error(request, f'Une erreur est survenue : {str(e)}')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = DCLPublicForm()

    return render(request, 'pages/demande_publique.html', {
        'form': form,
        'mapbox_token': settings.MAPBOX_ACCESS_TOKEN,
    })


def demande_confirmation(request, ref):
    """Page de confirmation après soumission d'une demande publique."""
    demande = get_object_or_404(DCL, ref=ref)
    return render(request, 'pages/demande_confirmation.html', {'demande': demande})
