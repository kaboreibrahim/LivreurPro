from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate,get_backends,get_user_model
from Auth.forms import *
from django.shortcuts import redirect
from Auth.models import VerificationCode
from django.contrib.auth.decorators import login_required
# view de creation de compte 
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import views as auth_views
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
#from taxi.models import P 
from django.core.exceptions import MultipleObjectsReturned

from django.contrib.auth import get_user_model
User = get_user_model()




class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None        
    
       
def register(request):
    
    USER_TYPE_CHOICES = [
        ('client', 'Client'),
        ('livreur', 'Livreur'),
        ('gestionnaire', 'Gestionnaire'),
]
    if request.method == 'POST':
        form = CustomForm(request.POST , request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('verify')  # Rediriger vers la page de vérification
    else:
        form = CustomForm()
    return render(request, 'registration/register.html', {'form': form, 'USER_TYPE_CHOICES': USER_TYPE_CHOICES})

# view de verification de creation de compte 

def verify(request):
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                verification_code = VerificationCode.objects.get(code=code)
                user = verification_code.user
                user.is_active = True
                user.is_verified = True
                user.save()
                verification_code.delete()  # Supprimer le code de vérification après validation
                
                # Obtenir le backend d'authentification utilisé
                backend = get_backends()[0]
                login(request, user, backend='accounts.auth_backends.EmailOrUsernameModelBackend')
                return redirect('login')
            except VerificationCode.DoesNotExist:
                form.add_error('code', 'Code invalide')
    else:
        form = VerificationForm()
    return render(request, 'registration/verify.html', {'form': form})

"""
# view de connexion """
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            try:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    if user.role == 'client':
                        messages.success(request, f'bienvenue {user.username} ')
                        return redirect('Client:Dashbord_client')
                    elif user.role == 'livreur':
                        messages.success(request, f'bienvenue {user.username}')
                        return redirect('index_livreur')
                    elif user.role == 'gestionnaire':
                        messages.success(request, f'bienvenue {user.username}')
                        return redirect('Gestionnaire:Dashbord_Gestionnaire')
                else:
                    form.add_error(None, 'Nom d\'utilisateur ou mot de passe incorrect')
            except MultipleObjectsReturned:
                form.add_error(None, 'Erreur : Plusieurs utilisateurs correspondent à ces informations.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})
 

@login_required
def deconnection(request):
    logout(request)
    # Redirige l'utilisateur vers une page après la déconnexion (par exemple la page d'accueil)
    messages.add_message(request, messages.SUCCESS, " A bientot  " )

    return redirect('Accueil')

#view reste password


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/rest/password_reset.html'

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            messages.error(self.request, "Cet email n'est associé à aucun compte utilisateur.")
            return self.form_invalid(form)
        return super().form_valid(form)
