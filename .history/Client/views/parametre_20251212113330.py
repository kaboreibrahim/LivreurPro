from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Client.decorators import role_required

@login_required
@role_required('client')
def parametres(request):
    """
    View for user settings page
    """
    context = {
        'title': 'Paramètres du compte',
    }
    return render(request, 'profile/parametres.html', context)

def change_password(request):
    """
    View for changing user password
    """
    if request.method == 'POST':
        # Add password change logic here
        messages.success(request, 'Votre mot de passe a été modifié avec succès.')
        return redirect('profile')
    
    context = {
        'title': 'Changer le mot de passe',
    }
    return render(request, 'profile/change_password.html', context)
