from django.urls import path
from . import views
app_name = 'users'
urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path('profile/', views.profile_view, name='profile'),
    path('address/add/', views.add_address, name='add_address'),
    path('address/delete/<int:pk>/', views.delete_address, name='delete_address'),
    path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
]
