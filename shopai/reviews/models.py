from django.db import models
from django.conf import settings

class Review(models.Model):
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i,i) for i in range(1,6)])
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_approved = models.BooleanField(default=True)
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product','user'); ordering = ['-created_at']

    def __str__(self): return f"{self.user.email} → {self.product.name} ({self.rating}★)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_rating()


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/')
