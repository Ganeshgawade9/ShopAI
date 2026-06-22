def cart_count(request):
    if request.user.is_authenticated:
        from .models import Cart
        c = Cart.objects.filter(user=request.user).first()
        return {'cart_count': c.item_count if c else 0}
    return {'cart_count': 0}
