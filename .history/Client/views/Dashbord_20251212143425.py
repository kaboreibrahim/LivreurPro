from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Client.decorators import role_required
@login_required
@role_required("client")
def Dashbord(request, *args, **kwargs):
    
    return render(request, 'pages/dashbord.html')


from django.shortcuts import render

def non_autorise(request):
    return render(request, 'pages/non_autorise.html')
