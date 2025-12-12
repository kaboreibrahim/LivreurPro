from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from Client.decorators import role_required
from Demande.models import DCL
import json

@login_required
@role_required('client')
def dashboard(request):
    # Get current user's orders
    orders = DCL.objects.filter(client=request.user)
    
    # Basic statistics
    total_orders = orders.count()
    completed_orders = orders.filter(statut='TERMINEE').count()
    in_progress_orders = orders.exclude(statut__in=['TERMINEE', 'ANNULEE']).count()
    cancelled_orders = orders.filter(statut='ANNULEE').count()
    
    # Monthly order data for the chart (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    # In Dashbord.py, update the monthly_data query to use PostgreSQL's TO_CHAR
    monthly_data = orders.filter(date_demande__gte=six_months_ago).extra(
        select={'month': "TO_CHAR(date_demande, 'YYYY-MM')"}
    ).values('month').annotate(count=Count('id')).order_by('month')
        
    # Prepare data for the chart
    months = [data['month'] for data in monthly_data]
    order_counts = [data['count'] for data in monthly_data]
    
    # Order status distribution for the pie chart
    status_distribution = orders.values('statut').annotate(count=Count('id'))
    status_labels = [dict(DCL.STATUT_CHOICES).get(item['statut'], item['statut']) for item in status_distribution]
    status_data = [item['count'] for item in status_distribution]
    
    context = {
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'in_progress_orders': in_progress_orders,
        'cancelled_orders': cancelled_orders,
        'months': json.dumps(months),
        'order_counts': json.dumps(order_counts),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
    }
    
    return render(request, 'pages/dashbord.html', context)

def non_autorise(request):
    return render(request, 'pages/non_autorise.html')
