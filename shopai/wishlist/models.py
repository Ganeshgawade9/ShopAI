from django.db import models
from django.conf import settings
class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField('store.Product', blank=True)
    def __str__(self): return f"Wishlist({self.user.email})"
