from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_vendor = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    dark_mode = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.username


class Address(models.Model):
    ADDRESS_TYPES = [('home','Home'),('work','Work'),('other','Other')]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='home')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=300)
    address_line2 = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='India')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name}, {self.city} - {self.pincode}"

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class OTPRecord(models.Model):
    OTP_TYPES = [('email','Email'),('phone','Phone'),('reset','Password Reset')]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    otp_type = models.CharField(max_length=10, choices=OTP_TYPES)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    @property
    def is_valid(self):
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()
