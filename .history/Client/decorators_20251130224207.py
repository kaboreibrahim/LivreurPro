from django.shortcuts import redirect
from django.contrib import messages

def role_required(role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')  # ou ta page de connexion

            if hasattr(request.user, "gestionnaire") and request.user.role == role:
                return view_func(request, *args, **kwargs)

            messages.error(request, "Vous n’êtes pas habilité à accéder à cette page.")
            return redirect('Client:non_autorise')
        return wrapper
    return decorator
