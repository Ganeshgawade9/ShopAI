from django.db import models
from django.utils.text import slugify
from django.urls import reverse
import uuid


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self): return self.name

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:category', kwargs={'slug': self.slug})


class Brand(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self): return self.name

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    vendor = models.ForeignKey('vendor.Vendor', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')

    name = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True, max_length=350)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    predicted_discount = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)

    views_count = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self): return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            self.slug = base
            n = 1
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{n}"; n += 1
        if not self.sku:
            self.sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    @property
    def discount_percent(self):
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0

    @property
    def is_in_stock(self): return self.stock > 0

    @property
    def is_low_stock(self): return 0 < self.stock <= self.low_stock_threshold

    @property
    def main_image(self):
        img = self.images.filter(is_primary=True).first()
        return img or self.images.first()

    def update_rating(self):
        from reviews.models import Review
        qs = Review.objects.filter(product=self, is_approved=True)
        if qs.exists():
            self.avg_rating = round(qs.aggregate(models.Avg('rating'))['rating__avg'], 2)
            self.review_count = qs.count()
        else:
            self.avg_rating = 0
            self.review_count = 0
        self.save(update_fields=['avg_rating','review_count'])


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self): return f"{self.product.name} img"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)   # e.g. Color
    value = models.CharField(max_length=100)  # e.g. Red
    price_modifier = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self): return f"{self.product.name} - {self.name}: {self.value}"


class RecentlyViewed(models.Model):
    from django.conf import settings
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recently_viewed')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user','product')
        ordering = ['-viewed_at']


class PurchaseHistory(models.Model):
    from django.conf import settings
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchase_history')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-purchased_at']
