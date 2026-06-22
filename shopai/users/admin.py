from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Address, OTPRecord

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email','username','full_name','is_vendor','is_email_verified','date_joined']
    list_filter = ['is_vendor','is_email_verified','is_staff']
    search_fields = ['email','username','first_name','last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('ShopAI', {'fields': ('phone','avatar','is_vendor','is_email_verified','dark_mode')}),
    )

admin.site.register(Address)
admin.site.register(OTPRecord)
