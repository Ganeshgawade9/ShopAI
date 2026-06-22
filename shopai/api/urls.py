from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', views.api_register, name='api_register'),
    path('auth/login/', views.api_login, name='api_login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', views.api_profile, name='api_profile'),
    path('cart/', views.api_cart, name='api_cart'),
    path('recommendations/', views.api_recommendations, name='api_recommendations'),
]
