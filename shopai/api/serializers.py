from rest_framework import serializers
from store.models import Product, Category, ProductImage
from orders.models import Order, OrderItem
from cart.models import Cart, CartItem
from django.contrib.auth import get_user_model
User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','slug','image']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','image','alt_text','is_primary']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)
    main_image_url = serializers.SerializerMethodField()
    discount_percent = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id','name','slug','price','compare_price','discount_percent',
                  'avg_rating','review_count','category_name','brand_name',
                  'main_image_url','is_in_stock','stock','is_featured','is_trending']

    def get_main_image_url(self, obj):
        img = obj.main_image
        if img and img.image:
            req = self.context.get('request')
            return req.build_absolute_uri(img.image.url) if req else img.image.url
        return None

class ProductDetailSerializer(ProductSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['description','short_description','sku','images']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id','product_name','product_sku','quantity','price','total']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    class Meta:
        model = Order
        fields = ['id','order_number','status','status_display','payment_method','payment_display',
                  'payment_status','subtotal','shipping_cost','tax','total','shipping_name',
                  'shipping_address','tracking_number','estimated_delivery','created_at','items']
        read_only_fields = ['order_number','status','total']

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()
    class Meta:
        model = CartItem
        fields = ['id','product','product_name','quantity','price','subtotal']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()
    class Meta:
        model = Cart
        fields = ['id','items','total','item_count']

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    class Meta:
        model = User
        fields = ['id','email','username','first_name','last_name','full_name','phone','is_vendor','is_email_verified']
