from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from LivreurV1.models import CustomUser

@login_required
def index_gestionnaire(request, *args, **kwargs):
    if request.user.is_authenticated:
        messages.add_message(
            request, messages.SUCCESS, f"Bienvenue, {request.user.first_name} {request.user.last_name} (Gestionnaire) !"
        )
    return render(request, 'index_gestionnaire.html' )

# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# import json

# @csrf_exempt
# @login_required
# def save_user_location(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             print(data)
#             latitude = data.get('latitude')
#             longitude = data.get('longitude')

#             if latitude is not None and longitude is not None:
#                 location = CustomUser.objects.create(
#                     user=request.user,
#                     latitude=latitude,
#                     longitude=longitude
#                 )
#                 return JsonResponse({"status": "success", "message": "Location saved successfully."}, status=200)
#             else:
#                 return JsonResponse({"status": "error", "message": "Invalid data."}, status=400)
#         except json.JSONDecodeError:
#             return JsonResponse({"status": "error", "message": "Invalid JSON."}, status=400)
#     return JsonResponse({"status": "error", "message": "Only POST method allowed."}, status=405)

