"""
Management command: python manage.py seed_data
Creates a superuser + demo categories/brands/products so the store isn't empty on first run.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from store.models import Category, Brand, Product

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with a superuser and demo store data"

    def handle(self, *args, **options):
        if not User.objects.filter(email="admin@shopai.com").exists():
            User.objects.create_superuser(
                username="admin", email="admin@shopai.com", password="admin123",
                first_name="Admin", last_name="ShopAI", is_email_verified=True,
            )
            self.stdout.write(self.style.SUCCESS("✓ Superuser created: admin@shopai.com / admin123"))
        else:
            self.stdout.write("Superuser already exists, skipping.")

        cats = ["Electronics", "Fashion", "Home & Kitchen", "Books", "Sports & Fitness", "Beauty & Care"]
        for name in cats:
            Category.objects.get_or_create(slug=slugify(name), defaults={"name": name})
        self.stdout.write(self.style.SUCCESS(f"✓ Categories: {Category.objects.count()}"))

        brands = ["Samsung", "Apple", "Nike", "Adidas", "OnePlus", "boAt", "Lakme", "Prestige"]
        for b in brands:
            Brand.objects.get_or_create(slug=slugify(b), defaults={"name": b})
        self.stdout.write(self.style.SUCCESS(f"✓ Brands: {Brand.objects.count()}"))

        sample = [
            ("iPhone 15 Pro Max", "electronics", "apple", 134900, 149900, True, True, 50),
            ("Samsung Galaxy S24", "electronics", "samsung", 79999, 89999, True, True, 30),
            ("Nike Air Max 270", "fashion", "nike", 9995, 12995, False, True, 100),
            ("OnePlus 12R", "electronics", "oneplus", 39999, 44999, True, False, 75),
            ("boAt Airdopes 141", "electronics", "boat", 1299, 2499, False, True, 200),
            ("Adidas Ultraboost 22", "fashion", "adidas", 14995, 17999, True, False, 60),
            ("Prestige Induction Cooktop", "home-kitchen", "prestige", 2499, 3199, False, True, 40),
            ("Lakme Lipstick Combo", "beauty-care", "lakme", 599, 899, True, False, 150),
            ("Classic Fiction Boxset", "books", None, 1499, 1999, False, False, 25),
            ("Yoga Mat Pro", "sports-fitness", None, 899, 1299, True, False, 80),
        ]
        created = 0
        for name, cat_slug, brand_slug, price, compare, feat, trend, stock in sample:
            cat = Category.objects.filter(slug=cat_slug).first()
            brand = Brand.objects.filter(slug=brand_slug).first() if brand_slug else None
            if not Product.objects.filter(name=name).exists():
                Product.objects.create(
                    name=name, category=cat, brand=brand, price=price, compare_price=compare,
                    stock=stock, is_featured=feat, is_trending=trend, is_active=True,
                    description=f"{name} — Premium quality, best-in-class performance and build quality. Trusted by thousands of happy customers across India.",
                    short_description=f"Experience the best of {name}.",
                    avg_rating=4.3, review_count=12, views_count=80, sales_count=25,
                )
                created += 1
        self.stdout.write(self.style.SUCCESS(f"✓ Products created this run: {created} (total: {Product.objects.count()})"))
        self.stdout.write(self.style.SUCCESS("\n🎉 Seed complete! Login at /admin/ with admin@shopai.com / admin123\n"))
