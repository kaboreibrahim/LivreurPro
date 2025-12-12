from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from Auth.models import CustomUser
from Demande.models import DCL
from Client.forms import (
    ProfileForm, 
    PasswordChangeForm
)

from django.contrib.auth import update_session_auth_hash


@login_required
def profile(request):
    
    return render(request, 'profile/profile.html')
 