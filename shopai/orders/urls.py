from django.urls import path
from . import views
app_name = 'orders'
urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('place/', views.place_order, name='place_order'),
    path('', views.order_list, name='order_list'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
    path('<int:pk>/razorpay/', views.razorpay_pay, name='razorpay_pay'),
    path('razorpay/callback/', views.razorpay_callback, name='razorpay_callback'),
    path('<int:pk>/stripe/', views.stripe_pay, name='stripe_pay'),
]
