from django.urls import path
from . import views
app_name = 'wishlist'
urlpatterns = [
    path('', views.wishlist_view, name='view'),
    path('toggle/<int:product_id>/', views.toggle_wishlist, name='toggle'),
    path('move-to-cart/<int:product_id>/', views.move_to_cart, name='move_to_cart'),
]
