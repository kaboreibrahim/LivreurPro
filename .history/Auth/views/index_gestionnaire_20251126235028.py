from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
 
@login_required
def index_gestionnaire(request, *args, **kwargs):
    if request.user.is_authenticated:
        messages.add_message(
            request, messages.SUCCESS, f"Bienvenue, {request.user.first_name} {request.user.last_name} (Gestionnaire) !"
        )
    return render(request, 'index_gestionnaire.html' )
 