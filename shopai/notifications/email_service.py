from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation(order):
    try:
        msg = (f"Dear {order.user.first_name or order.user.username},\n\n"
               f"Your order #{order.order_number} is confirmed!\n"
               f"Total: ₹{order.total}\n"
               f"Payment: {order.get_payment_method_display()}\n"
               f"Est. Delivery: {order.estimated_delivery}\n\n"
               f"Thank you for shopping with ShopAI!")
        send_mail(f'Order #{order.order_number} Confirmed — ShopAI', msg,
                  settings.DEFAULT_FROM_EMAIL, [order.user.email], fail_silently=True)
    except Exception as e:
        print(f"[Email] {e}")

def send_shipping_update(order):
    try:
        send_mail(f'Order #{order.order_number} Update — ShopAI',
                  f"Your order #{order.order_number} is now: {order.get_status_display()}",
                  settings.DEFAULT_FROM_EMAIL, [order.user.email], fail_silently=True)
    except Exception as e:
        print(f"[Email] {e}")

def send_otp_email(email, code):
    try:
        send_mail('ShopAI — Email Verification OTP',
                  f"Your OTP is: {code}\nExpires in 10 minutes.",
                  settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True)
    except Exception as e:
        print(f"[Email] {e}")

def send_sms(phone, message):
    try:
        from twilio.rest import Client
        Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN).messages.create(
            body=message, from_=settings.TWILIO_PHONE_NUMBER, to=phone)
    except Exception as e:
        print(f"[SMS] {e}")
