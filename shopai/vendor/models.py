from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Vendor(models.Model):
    STATUS = [('pending','Pending'),('approved','Approved'),('suspended','Suspended')]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='vendors/', null=True, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    gst_number = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.business_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.business_name)
        super().save(*args, **kwargs)
