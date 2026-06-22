from django.contrib import admin
from .models import Vendor
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['business_name','user','status','commission_rate','created_at']
    list_editable = ['status']; list_filter = ['status']
