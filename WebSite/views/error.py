from django.shortcuts import render

def custom_404_view(request, exception):
    return render(request, 'error/404.html', status=404)

def custom_500_view(request):
    return render(request, 'error/500.html', status=500)
