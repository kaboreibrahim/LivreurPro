from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum, Avg
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
    pending_orders = orders.filter(statut='EN_ATTENTE').count()
    
    # Additional statistics
    total_spent = orders.filter(cout_livraison__isnull=False).aggregate(
        total=Sum('cout_livraison')
    )['total'] or 0
    
    avg_delivery_cost = orders.filter(cout_livraison__isnull=False).aggregate(
        avg=Avg('cout_livraison')
    )['avg'] or 0
    
    # Recent orders (last 5)
    recent_orders = orders.order_by('-date_demande')[:5]
    
    # Pending orders details
    pending_orders_list = orders.filter(statut='EN_ATTENTE').order_by('-date_demande')[:5]
    
    # Monthly order data for the chart (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_data = orders.filter(date_demande__gte=six_months_ago).extra(
        select={'month': "TO_CHAR(date_demande, 'YYYY-MM')"}
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    # Prepare data for the monthly chart
    months = [data['month'] for data in monthly_data]
    order_counts = [data['count'] for data in monthly_data]
    
    # Order status distribution for the pie chart
    status_distribution = orders.values('statut').annotate(count=Count('id'))
    status_labels = [dict(DCL.STATUT_CHOICES).get(item['statut'], item['statut']) for item in status_distribution]
    status_data = [item['count'] for item in status_distribution]
    
    # Weekly trend (last 4 weeks)
    four_weeks_ago = timezone.now() - timedelta(days=28)
    weekly_data = []
    for i in range(4):
        week_start = four_weeks_ago + timedelta(days=i*7)
        week_end = week_start + timedelta(days=7)
        week_count = orders.filter(
            date_demande__gte=week_start,
            date_demande__lt=week_end
        ).count()
        weekly_data.append(week_count)
    
    # Type de course distribution
    course_types = orders.values('type_course').annotate(count=Count('id'))
    course_type_labels = [dict(DCL.TYPE_COURSE_CHOICES).get(item['type_course'], item['type_course']) for item in course_types]
    course_type_data = [item['count'] for item in course_types]
    
    context = {
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'in_progress_orders': in_progress_orders,
        'cancelled_orders': cancelled_orders,
        'pending_orders': pending_orders,
        'total_spent': round(total_spent, 2),
        'avg_delivery_cost': round(avg_delivery_cost, 2),
        # 'total_distance': round(total_distance, 2),
        'recent_orders': recent_orders,
        'pending_orders_list': pending_orders_list,
        'months': json.dumps(months),
        'order_counts': json.dumps(order_counts),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
        'weekly_data': json.dumps(weekly_data),
        'course_type_labels': json.dumps(course_type_labels),
        'course_type_data': json.dumps(course_type_data),
    }
    
    return render(request, 'pages/dashbord.html', context)

def non_autorise(request):
    return render(request, 'pages/non_autorise.html')