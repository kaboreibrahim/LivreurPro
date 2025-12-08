from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def DashbordGestionnaire(request, *args, **kwargs):
    
    return render(request, 'pages/dashbord.html')
