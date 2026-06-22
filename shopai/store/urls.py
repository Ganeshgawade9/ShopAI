from django.urls import path
from . import views
app_name = 'store'
urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('trending/', views.trending_view, name='trending'),
    path('search/suggestions/', views.search_suggestions, name='suggestions'),
]
