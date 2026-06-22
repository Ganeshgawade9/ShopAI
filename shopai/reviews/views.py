from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review, ReviewImage
from store.models import Product

@login_required
def add_review(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, 'You already reviewed this product.')
        return redirect('store:product_detail', slug=product_slug)
    if request.method == 'POST':
        from orders.models import OrderItem
        is_verified = OrderItem.objects.filter(order__user=request.user, product=product).exists()
        review = Review.objects.create(
            product=product, user=request.user,
            rating=int(request.POST.get('rating',5)),
            title=request.POST.get('title',''),
            body=request.POST.get('body',''),
            is_verified_purchase=is_verified,
        )
        for img in request.FILES.getlist('images'):
            ReviewImage.objects.create(review=review, image=img)
        messages.success(request, 'Review submitted! Thank you.')
    return redirect('store:product_detail', slug=product_slug)

@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    slug = review.product.slug
    review.delete()
    messages.success(request, 'Review deleted.')
    return redirect('store:product_detail', slug=slug)
