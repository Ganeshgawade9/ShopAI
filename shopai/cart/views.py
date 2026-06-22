from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Cart, CartItem
from store.models import Product, ProductVariant

def _cart(user):
    c, _ = Cart.objects.get_or_create(user=user)
    return c

@login_required
def cart_view(request):
    return render(request, 'cart/cart.html', {'cart': _cart(request.user)})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    qty = int(request.POST.get('quantity', 1))
    if product.stock < qty:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Insufficient stock'})
        messages.error(request, 'Insufficient stock.')
        return redirect('store:product_detail', slug=product.slug)
    cart = _cart(request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, variant=None, defaults={'quantity': qty})
    if not created:
        item.quantity += qty; item.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': f'Added to cart!', 'cart_count': cart.item_count})
    messages.success(request, f'{product.name} added to cart!')
    return redirect('store:product_detail', slug=product.slug)

@login_required
def remove_from_cart(request, item_id):
    get_object_or_404(CartItem, id=item_id, cart__user=request.user).delete()
    cart = _cart(request.user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.item_count, 'cart_total': str(cart.total)})
    messages.success(request, 'Item removed.')
    return redirect('cart:view')

@login_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    qty = int(request.POST.get('quantity', 1))
    if qty < 1: item.delete()
    else: item.quantity = qty; item.save()
    cart = _cart(request.user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.item_count, 'cart_total': str(cart.total),
                             'item_subtotal': str(item.subtotal if qty >= 1 else 0)})
    return redirect('cart:view')
