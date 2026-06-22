from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderItem, OrderStatusHistory
from cart.models import Cart
from store.models import PurchaseHistory


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:view')
    addresses = request.user.addresses.all()
    default_addr = addresses.filter(is_default=True).first() or addresses.first()
    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'addresses': addresses,
        'default_addr': default_addr,
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
    })


@login_required
def place_order(request):
    if request.method != 'POST':
        return redirect('orders:checkout')
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        return redirect('cart:view')

    addr_id = request.POST.get('address_id')
    payment_method = request.POST.get('payment_method', 'cod')

    from users.models import Address
    try:
        addr = Address.objects.get(id=addr_id, user=request.user)
    except Address.DoesNotExist:
        messages.error(request, 'Please select a delivery address.')
        return redirect('orders:checkout')

    subtotal = cart.total
    shipping = 0 if subtotal >= 499 else 49
    tax = round(subtotal * 18 / 100, 2)
    total = round(subtotal + shipping + tax, 2)

    order = Order.objects.create(
        user=request.user,
        shipping_name=addr.full_name,
        shipping_phone=addr.phone,
        shipping_address=f"{addr.address_line1}, {addr.city}, {addr.state} - {addr.pincode}, {addr.country}",
        subtotal=subtotal, shipping_cost=shipping, tax=tax, total=total,
        payment_method=payment_method,
        estimated_delivery=timezone.now().date() + timedelta(days=5),
    )
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order, product=item.product,
            product_name=item.product.name, product_sku=item.product.sku,
            quantity=item.quantity, price=item.price,
        )
        # Deduct stock
        item.product.stock = max(0, item.product.stock - item.quantity)
        item.product.sales_count += item.quantity
        item.product.save(update_fields=['stock','sales_count'])
        # Record purchase for AI
        PurchaseHistory.objects.create(user=request.user, product=item.product, quantity=item.quantity)

    OrderStatusHistory.objects.create(order=order, status='confirmed')
    order.status = 'confirmed'
    order.save(update_fields=['status'])
    cart.items.all().delete()

    # Email notification
    from notifications.email_service import send_order_confirmation
    send_order_confirmation(order)

    if payment_method == 'razorpay':
        return redirect('orders:razorpay_pay', pk=order.pk)
    elif payment_method == 'stripe':
        return redirect('orders:stripe_pay', pk=order.pk)

    messages.success(request, f'Order #{order.order_number} placed successfully!')
    return redirect('orders:order_detail', pk=order.pk)


@login_required
def razorpay_pay(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    try:
        import razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        rz_order = client.order.create({'amount': int(order.total*100), 'currency':'INR', 'payment_capture':1})
        order.razorpay_order_id = rz_order['id']
        order.save(update_fields=['razorpay_order_id'])
        return render(request, 'orders/razorpay_payment.html', {
            'order': order, 'rz_order': rz_order, 'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
        })
    except Exception as e:
        messages.warning(request, f'Razorpay not configured: {e}. Treating as COD.')
        order.payment_status = 'pending'
        order.save()
        messages.success(request, f'Order #{order.order_number} placed (COD)!')
        return redirect('orders:order_detail', pk=order.pk)


@csrf_exempt
def razorpay_callback(request):
    if request.method == 'POST':
        try:
            import razorpay
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature({
                'razorpay_order_id': request.POST.get('razorpay_order_id'),
                'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
                'razorpay_signature': request.POST.get('razorpay_signature'),
            })
            order = Order.objects.get(razorpay_order_id=request.POST.get('razorpay_order_id'))
            order.payment_status = 'paid'
            order.payment_id = request.POST.get('razorpay_payment_id')
            order.save()
            messages.success(request, 'Payment successful!')
            return redirect('orders:order_detail', pk=order.pk)
        except Exception as e:
            messages.error(request, f'Payment verification failed: {e}')
    return redirect('orders:order_list')


@login_required
def stripe_pay(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if request.method == 'POST':
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100), currency='inr',
                metadata={'order_id': order.id}
            )
            order.payment_status = 'paid'
            order.payment_id = intent.id
            order.save()
            messages.success(request, 'Payment successful!')
            return redirect('orders:order_detail', pk=order.pk)
        except Exception as e:
            messages.warning(request, f'Stripe not configured: {e}. Treating as COD.')
            return redirect('orders:order_detail', pk=order.pk)
    return render(request, 'orders/stripe_payment.html', {'order': order, 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/order_detail.html', {
        'order': order, 'status_history': order.status_history.all()
    })


@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.status in ['pending','confirmed']:
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save(update_fields=['stock'])
        order.status = 'cancelled'
        order.save(update_fields=['status'])
        OrderStatusHistory.objects.create(order=order, status='cancelled', note='Cancelled by customer')
        messages.success(request, 'Order cancelled successfully.')
    else:
        messages.error(request, 'Cannot cancel this order at current stage.')
    return redirect('orders:order_detail', pk=pk)
