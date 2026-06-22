from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vendor
from store.models import Product
from orders.models import OrderItem

@login_required
def vendor_register(request):
    if hasattr(request.user, 'vendor_profile'):
        return redirect('vendor:dashboard')
    if request.method == 'POST':
        Vendor.objects.create(
            user=request.user,
            business_name=request.POST.get('business_name',''),
            phone=request.POST.get('phone',''),
            email=request.POST.get('email', request.user.email),
            address=request.POST.get('address',''),
            gst_number=request.POST.get('gst_number',''),
        )
        request.user.is_vendor = True
        request.user.save(update_fields=['is_vendor'])
        messages.success(request, 'Vendor registration submitted! Awaiting approval.')
        return redirect('vendor:dashboard')
    return render(request, 'vendor/register.html')

@login_required
def vendor_dashboard(request):
    if not hasattr(request.user, 'vendor_profile'):
        return redirect('vendor:register')
    vendor = request.user.vendor_profile
    products = Product.objects.filter(vendor=vendor)
    recent_orders = OrderItem.objects.filter(product__vendor=vendor).select_related('order','product').order_by('-order__created_at')[:10]
    return render(request, 'vendor/dashboard.html', {
        'vendor': vendor, 'products': products, 'recent_orders': recent_orders,
        'total_products': products.count(), 'total_orders': recent_orders.count(),
    })
