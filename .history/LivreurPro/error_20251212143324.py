from django.shortcuts import render
from django.template import RequestContext

def custom_page_not_found(request, exception, template_name='error/404.html'):
    context = {}
    context['title'] = 'Page non trouvée (404)'
    context['error_code'] = '404'
    context['error_message'] = 'La page que vous recherchez est introuvable.'
    return render(request, template_name, context, status=404)

def custom_permission_denied(request, exception, template_name='error/403.html'):
    context = {}
    context['title'] = 'Accès refusé (403)'
    context['error_code'] = '403'
    context['error_message'] = 'Vous n\'avez pas la permission d\'accéder à cette page.'
    return render(request, template_name, context, status=403)

def custom_bad_request(request, exception, template_name='error/400.html'):
    context = {}
    context['title'] = 'Requête incorrecte (400)'
    context['error_code'] = '400'
    context['error_message'] = 'La requête ne peut être traitée en raison d\'une erreur de syntaxe.'
    return render(request, template_name, context, status=400)

def custom_server_error(request, template_name='error/500.html'):
    context = {}
    context['title'] = 'Erreur serveur (500)'
    context['error_code'] = '500'
    context['error_message'] = 'Une erreur serveur s\'est produite. Veuillez réessayer plus tard.'
    return render(request, template_name, context, status=500)
