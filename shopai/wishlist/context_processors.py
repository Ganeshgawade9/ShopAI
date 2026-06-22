def wishlist_count(request):
    if request.user.is_authenticated:
        from .models import Wishlist
        wl = Wishlist.objects.filter(user=request.user).first()
        return {'wishlist_count': wl.products.count() if wl else 0}
    return {'wishlist_count': 0}
