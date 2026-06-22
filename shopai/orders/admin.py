from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory

class ItemInline(admin.TabularInline):
    model = OrderItem; extra = 0; readonly_fields = ['total']

class HistoryInline(admin.TabularInline):
    model = OrderStatusHistory; extra = 0; readonly_fields = ['created_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','user','status','payment_method','payment_status','total','created_at']
    list_filter = ['status','payment_method','payment_status']
    search_fields = ['order_number','user__email']
    list_editable = ['status','payment_status']
    readonly_fields = ['order_number']
    inlines = [ItemInline, HistoryInline]

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            OrderStatusHistory.objects.create(order=obj, status=obj.status, note='Updated by admin')
            from notifications.email_service import send_shipping_update
            send_shipping_update(obj)
        super().save_model(request, obj, form, change)
