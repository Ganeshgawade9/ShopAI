from django.contrib import admin
from .models import Cart, CartItem
class ItemInline(admin.TabularInline):
    model = CartItem; extra = 0
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user','item_count','total']; inlines = [ItemInline]
