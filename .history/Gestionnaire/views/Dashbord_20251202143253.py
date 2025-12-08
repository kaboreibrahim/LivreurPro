from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.http import JsonResponse
from Livreur.models import Livreur
from django.db.models import Case, When, IntegerField
@login_required
def DashbordGestionnaire(request, *args, **kwargs):
    
    return render(request, 'pages/dashbord_gestionnaire.html')





