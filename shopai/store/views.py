from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Min, Max
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Product, Category, Brand, RecentlyViewed, PurchaseHistory
from .recommendation import get_recommendations, get_similar_products


def index(request):
    featured = Product.objects.filter(is_active=True, is_featured=True)[:8]
    trending = Product.objects.filter(is_active=True, is_trending=True)[:8]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.filter(is_active=True, parent=None)[:8]
    recommendations = []
    recently_viewed = []
    if request.user.is_authenticated:
        recommendations = get_recommendations(request.user)
        recently_viewed = RecentlyViewed.objects.filter(user=request.user).select_related('product')[:8]
    return render(request, 'store/index.html', {
        'featured': featured, 'trending': trending, 'new_arrivals': new_arrivals,
        'categories': categories, 'recommendations': recommendations, 'recently_viewed': recently_viewed,
    })


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('category','brand')
    query = request.GET.get('q','')
    if query:
        products = products.filter(Q(name__icontains=query)|Q(description__icontains=query)|Q(brand__name__icontains=query)).distinct()
    cat_slug = request.GET.get('category','')
    brand_id = request.GET.get('brand','')
    min_price = request.GET.get('min_price','')
    max_price = request.GET.get('max_price','')
    min_rating = request.GET.get('rating','')
    in_stock = request.GET.get('in_stock','')
    sort = request.GET.get('sort','-created_at')
    if cat_slug: products = products.filter(category__slug=cat_slug)
    if brand_id: products = products.filter(brand_id=brand_id)
    if min_price: products = products.filter(price__gte=min_price)
    if max_price: products = products.filter(price__lte=max_price)
    if min_rating: products = products.filter(avg_rating__gte=min_rating)
    if in_stock: products = products.filter(stock__gt=0)
    sort_map = {'price_asc':'price','price_desc':'-price','rating':'-avg_rating','popular':'-sales_count','newest':'-created_at'}
    products = products.order_by(sort_map.get(sort,'-created_at'))
    paginator = Paginator(products, 24)
    page_obj = paginator.get_page(request.GET.get('page',1))
    return render(request, 'store/product_list.html', {
        'products': page_obj, 'query': query, 'total': paginator.count,
        'categories': Category.objects.filter(is_active=True),
        'brands': Brand.objects.filter(is_active=True),
        'sel_cat': cat_slug, 'sel_brand': brand_id,
        'sel_min': min_price, 'sel_max': max_price,
        'sel_rating': min_rating, 'sel_stock': in_stock, 'sel_sort': sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    Product.objects.filter(pk=product.pk).update(views_count=product.views_count+1)
    if request.user.is_authenticated:
        RecentlyViewed.objects.update_or_create(user=request.user, product=product)
    from reviews.models import Review
    reviews = Review.objects.filter(product=product, is_approved=True).select_related('user')[:15]
    similar = get_similar_products(product)
    from orders.models import OrderItem
    from django.db.models import Count
    also_ids = OrderItem.objects.filter(order__items__product=product).exclude(product=product)\
        .values('product_id').annotate(c=Count('id')).order_by('-c').values_list('product_id',flat=True)[:6]
    also_bought = Product.objects.filter(id__in=also_ids, is_active=True)
    return render(request, 'store/product_detail.html', {
        'product': product, 'reviews': reviews,
        'similar_products': similar, 'also_bought': also_bought,
    })


def category_view(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=cat, is_active=True)
    page_obj = Paginator(products, 24).get_page(request.GET.get('page',1))
    return render(request, 'store/category.html', {'category': cat, 'products': page_obj})


def trending_view(request):
    products = Product.objects.filter(is_active=True, is_trending=True)
    return render(request, 'store/trending.html', {'products': products})


def search_suggestions(request):
    q = request.GET.get('q','').strip()
    if len(q) < 2:
        return JsonResponse({'products':[],'categories':[]})
    prods = list(Product.objects.filter(name__icontains=q,is_active=True).values('slug','name','price')[:7])
    cats = list(Category.objects.filter(name__icontains=q,is_active=True).values('slug','name')[:3])
    return JsonResponse({'products': prods, 'categories': cats})
