from django.urls import path
from Demande.views.notifications import notifications_list, marquer_lu, marquer_tout_lu

urlpatterns = [
    path('', notifications_list, name='liste'),
    path('<int:pk>/lu/', marquer_lu, name='marquer_lu'),
    path('tout-lu/', marquer_tout_lu, name='marquer_tout_lu'),
]
