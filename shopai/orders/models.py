from django.db import models
from django.conf import settings
import uuid

class Order(models.Model):
    STATUS = [
        ('pending','Pending'),('confirmed','Confirmed'),('packed','Packed'),
        ('shipped','Shipped'),('out_for_delivery','Out for Delivery'),
        ('delivered','Delivered'),('cancelled','Cancelled'),('refunded','Refunded'),
    ]
    PAYMENT_STATUS = [('pending','Pending'),('paid','Paid'),('failed','Failed'),('refunded','Refunded')]
    PAYMENT_METHOD = [('razorpay','Razorpay'),('stripe','Stripe'),('paypal','PayPal'),('cod','Cash on Delivery')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')

    shipping_name = models.CharField(max_length=200)
    shipping_phone = models.CharField(max_length=15)
    shipping_address = models.TextField()

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_id = models.CharField(max_length=200, blank=True)
    razorpay_order_id = models.CharField(max_length=200, blank=True)

    tracking_number = models.CharField(max_length=100, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: ordering = ['-created_at']

    def __str__(self): return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    STEP_ORDER = ['confirmed','packed','shipped','out_for_delivery','delivered']

    @property
    def status_steps(self):
        try: cur = self.STEP_ORDER.index(self.status)
        except ValueError: cur = -1
        return [(s, i <= cur) for i, s in enumerate(self.STEP_ORDER)]

    @property
    def status_percent(self):
        try: return int((self.STEP_ORDER.index(self.status) / (len(self.STEP_ORDER)-1)) * 100)
        except ValueError: return 0


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('store.Product', on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=300)
    product_sku = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self): return f"{self.product_name} x{self.quantity}"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']
