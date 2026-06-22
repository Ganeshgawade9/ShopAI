from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from datetime import timedelta
import json
from orders.models import Order, OrderItem
from store.models import Product
from django.contrib.auth import get_user_model
User = get_user_model()

@staff_member_required
def dashboard(request):
    now = timezone.now()
    total_revenue = Order.objects.filter(payment_status='paid').aggregate(t=Sum('total'))['t'] or 0
    total_orders = Order.objects.count()
    active_users = User.objects.filter(last_login__gte=now-timedelta(days=30)).count()
    pending_orders = Order.objects.filter(status='pending').count()

    monthly = (Order.objects.filter(payment_status='paid', created_at__gte=now-timedelta(days=180))
               .annotate(month=TruncMonth('created_at')).values('month')
               .annotate(rev=Sum('total'), cnt=Count('id')).order_by('month'))
    monthly_labels = json.dumps([r['month'].strftime('%b %Y') for r in monthly])
    monthly_data = json.dumps([float(r['rev']) for r in monthly])

    daily = (Order.objects.filter(created_at__gte=now-timedelta(days=7))
             .annotate(day=TruncDay('created_at')).values('day').annotate(cnt=Count('id')).order_by('day'))
    daily_labels = json.dumps([r['day'].strftime('%d %b') for r in daily])
    daily_data = json.dumps([r['cnt'] for r in daily])

    top_products = (OrderItem.objects.values('product__name','product_id')
                    .annotate(qty=Sum('quantity'), rev=Sum('total')).order_by('-qty')[:10])

    status_data = Order.objects.values('status').annotate(cnt=Count('id'))
    status_labels = json.dumps([s['status'].replace('_',' ').title() for s in status_data])
    status_counts = json.dumps([s['cnt'] for s in status_data])

    low_stock = Product.objects.filter(stock__lte=5, is_active=True).order_by('stock')[:10]

    return render(request, 'analytics/dashboard.html', {
        'total_revenue': total_revenue, 'total_orders': total_orders,
        'active_users': active_users, 'pending_orders': pending_orders,
        'monthly_labels': monthly_labels, 'monthly_data': monthly_data,
        'daily_labels': daily_labels, 'daily_data': daily_data,
        'top_products': top_products, 'status_labels': status_labels,
        'status_counts': status_counts, 'low_stock': low_stock,
    })
