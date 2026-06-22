from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate, get_user_model
from store.models import Product, Category
from orders.models import Order
from cart.models import Cart, CartItem
from .serializers import (ProductSerializer, ProductDetailSerializer, CategorySerializer,
                           OrderSerializer, CartSerializer, UserSerializer)
User = get_user_model()

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category','brand')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category','brand','is_featured','is_trending']
    search_fields = ['name','description','brand__name']
    ordering_fields = ['price','avg_rating','sales_count','created_at']

    def get_serializer_class(self):
        return ProductDetailSerializer if self.action == 'retrieve' else ProductSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        return Response(ProductSerializer(self.get_queryset().filter(is_featured=True)[:8], many=True).data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        return Response(ProductSerializer(self.get_queryset().filter(is_trending=True)[:8], many=True).data)

    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        from store.recommendation import get_similar_products
        return Response(ProductSerializer(get_similar_products(self.get_object()), many=True).data)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    email = request.data.get('email','')
    password = request.data.get('password','')
    username = request.data.get('username', email.split('@')[0])
    if not email or not password:
        return Response({'error':'Email and password required'}, status=400)
    if User.objects.filter(email=email).exists():
        return Response({'error':'Email already registered'}, status=400)
    user = User.objects.create_user(username=username, email=email, password=password)
    refresh = RefreshToken.for_user(user)
    return Response({'user': UserSerializer(user).data, 'access': str(refresh.access_token), 'refresh': str(refresh)}, status=201)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    email = request.data.get('email','')
    password = request.data.get('password','')
    user = authenticate(request, username=email, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({'user': UserSerializer(user).data, 'access': str(refresh.access_token), 'refresh': str(refresh)})
    return Response({'error':'Invalid credentials'}, status=401)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_profile(request):
    return Response(UserSerializer(request.user).data)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def api_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if request.method == 'GET':
        return Response(CartSerializer(cart).data)
    pid = request.data.get('product_id')
    qty = int(request.data.get('quantity',1))
    try:
        product = Product.objects.get(id=pid, is_active=True)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product, variant=None, defaults={'quantity':qty})
        if not created: item.quantity += qty; item.save()
        return Response({'message': 'Added to cart', 'cart': CartSerializer(cart).data})
    except Product.DoesNotExist:
        return Response({'error':'Product not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_recommendations(request):
    from store.recommendation import get_recommendations
    return Response(ProductSerializer(get_recommendations(request.user), many=True).data)
