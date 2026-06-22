from django.contrib import admin
from .models import Review, ReviewImage
class ImgInline(admin.TabularInline):
    model = ReviewImage; extra = 0
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product','user','rating','is_approved','is_verified_purchase','created_at']
    list_filter = ['rating','is_approved']; list_editable = ['is_approved']
    inlines = [ImgInline]
