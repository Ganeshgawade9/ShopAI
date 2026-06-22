from django.db import models
from django.conf import settings

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return f"Cart({self.user.email})"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE)
    variant = models.ForeignKey('store.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart','product','variant')

    @property
    def price(self):
        p = self.product.price
        if self.variant: p += self.variant.price_modifier
        return p

    @property
    def subtotal(self): return self.price * self.quantity
