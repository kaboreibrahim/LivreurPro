from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from Livreur.models import Livreur

@login_required
def DashbordLivreur(request, *args, **kwargs):
    
    return render(request, 'pages/dashbord_livreur.html')



