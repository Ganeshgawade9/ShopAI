from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Wishlist
from store.models import Product

@login_required
def wishlist_view(request):
    wl, _ = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'wishlist/wishlist.html', {'wishlist': wl})

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wl, _ = Wishlist.objects.get_or_create(user=request.user)
    if product in wl.products.all():
        wl.products.remove(product); added = False
    else:
        wl.products.add(product); added = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'added': added, 'count': wl.products.count()})
    return redirect('wishlist:view')

@login_required
def move_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wl, _ = Wishlist.objects.get_or_create(user=request.user)
    wl.products.remove(product)
    from cart.models import Cart, CartItem
    cart, _ = Cart.objects.get_or_create(user=request.user)
    CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity':1})
    return redirect('cart:view')
