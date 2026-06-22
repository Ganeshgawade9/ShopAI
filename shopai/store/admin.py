from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, ProductVariant, RecentlyViewed, PurchaseHistory

class ImgInline(admin.TabularInline):
    model = ProductImage; extra = 1

class VarInline(admin.TabularInline):
    model = ProductVariant; extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','category','brand','price','stock','is_active','is_featured','is_trending','sales_count']
    list_filter = ['is_active','is_featured','is_trending','category']
    search_fields = ['name','sku']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active','is_featured','is_trending','stock']
    readonly_fields = ['views_count','sales_count','avg_rating','review_count','sku']
    inlines = [ImgInline, VarInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','parent','is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']

admin.site.register(Brand)
admin.site.register(RecentlyViewed)
admin.site.register(PurchaseHistory)
