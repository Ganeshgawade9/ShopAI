from django.urls import path
from . import views
app_name = 'vendor'
urlpatterns = [
    path('register/', views.vendor_register, name='register'),
    path('dashboard/', views.vendor_dashboard, name='dashboard'),
]
