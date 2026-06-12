from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from Demande.models import Notification


@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(
        destinataire=request.user
    ).select_related('demande').order_by('-date_creation')[:50]

    base_template_map = {
        'client': 'base.html',
        'livreur': 'base_livreur.html',
        'gestionnaire': 'base_gestionnaire.html',
    }
    base_template = base_template_map.get(request.user.role, 'base.html')

    return render(request, 'notifications/liste.html', {
        'notifications': notifications,
        'base_template': base_template,
    })


@login_required
@require_POST
def marquer_lu(request, pk):
    notif = get_object_or_404(Notification, pk=pk, destinataire=request.user)
    notif.lu = True
    notif.save(update_fields=['lu'])
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    if notif.lien:
        return redirect(notif.lien)
    return redirect('notifications:liste')


@login_required
@require_POST
def marquer_tout_lu(request):
    Notification.objects.filter(destinataire=request.user, lu=False).update(lu=True)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    referer = request.META.get('HTTP_REFERER', '')
    return redirect(referer) if referer else redirect('notifications:liste')
