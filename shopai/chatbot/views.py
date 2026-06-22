import re, json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

RULES = [
    (r'\b(hi|hello|hey|namaste|hlo)\b', "Hello! 👋 Welcome to ShopAI! I can help with products, orders, shipping, returns, and more. What do you need?"),
    (r'\border.*(status|track|where|update)\b|track.*order', "To track your order, go to **My Orders** section. Or share your order number like ORD-XXXXXXXX and I'll check for you!"),
    (r'\breturn|refund|exchange|replace', "📦 **Return Policy:**\n- Return within 7 days of delivery\n- Items must be unused & original packaging\n- Refund processed in 3–5 business days\n- Initiate from My Orders section"),
    (r'\bshipping|deliver|dispatch|courier', "🚚 **Shipping Info:**\n- FREE delivery on orders ₹499+\n- Standard: 3–7 business days\n- Express delivery: +₹99\n- Live tracking available in My Orders"),
    (r'\bpayment|pay|razorpay|stripe|paypal|upi|cod|cash on delivery', "💳 **Payment Options:**\n- Razorpay (UPI, Cards, Net Banking, Wallets)\n- Stripe (International Cards)\n- PayPal\n- Cash on Delivery (COD)"),
    (r'\bdiscount|coupon|offer|promo|sale|deal', "🎉 Check our **Sale** section for live offers! New users get 10% off on first order. Subscribe to newsletter for exclusive codes."),
    (r'\bcontact|support|help|call|email|complaint', "📞 **Contact Us:**\n- Email: support@shopai.com\n- Phone: +91-1234567890\n- Hours: Mon–Sat, 9AM–6PM IST\n- Or chat here anytime!"),
    (r'\bcancell?|cancel order', "You can cancel an order from **My Orders** if it's in Pending or Confirmed status. Once shipped, cancellation is not possible."),
    (r'\bwishlist|saved|favorite', "❤️ You can save products to your Wishlist by clicking the heart icon on any product. Access it from the navbar."),
    (r'\bvendor|sell|seller|register as seller', "🏪 Want to sell on ShopAI? Click **Sell on ShopAI** in the footer or go to /vendor/register/ to become a vendor!"),
    (r'\b(bye|goodbye|thanks|thank you|thx|dhanyawad)\b', "Thank you for shopping with ShopAI! 🛍️ Have a great day! Feel free to come back anytime."),
    (r'\bprice|cost|how much|kitna', "You can use the Price filter on the Products page to find items in your budget. Also check for discounted items in Sale section!"),
]

def rule_response(msg):
    msg_lower = msg.lower()
    for pattern, reply in RULES:
        if re.search(pattern, msg_lower):
            return reply
    return None

def order_lookup(msg, user):
    match = re.search(r'ORD-[A-Z0-9]{8,}', msg.upper())
    if match and user.is_authenticated:
        from orders.models import Order
        order = Order.objects.filter(order_number=match.group(), user=user).first()
        if order:
            return (f"📦 **Order {order.order_number}**\n"
                    f"- Status: **{order.get_status_display()}**\n"
                    f"- Total: ₹{order.total}\n"
                    f"- Payment: {order.get_payment_method_display()}\n"
                    f"- Est. Delivery: {order.estimated_delivery or 'N/A'}")
        return "I couldn't find that order. Make sure you're logged in and the order number is correct."
    return None

def product_search(msg):
    patterns = [r'(?:looking for|find|search|buy|price of|show me)\s+(.+)', r'(?:do you have|is there)\s+(.+)']
    for p in patterns:
        m = re.search(p, msg.lower())
        if m:
            query = m.group(1).strip().rstrip('?')
            from store.models import Product
            products = Product.objects.filter(name__icontains=query, is_active=True)[:4]
            if products:
                lines = [f"🛍️ Found products for **'{query}'**:"]
                for p in products:
                    stock = '✅ In Stock' if p.is_in_stock else '❌ Out of Stock'
                    lines.append(f"- **{p.name}** — ₹{p.price} ({stock})")
                return '\n'.join(lines)
    return None

def openai_fallback(msg, history):
    from django.conf import settings
    if not settings.OPENAI_API_KEY:
        return "I'm not sure about that. Please contact our support team at support@shopai.com or call +91-1234567890."
    try:
        import urllib.request, urllib.error
        payload = json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role":"system","content":"You are ShopAI customer support. Be concise and helpful. Answer questions about products, orders, shipping, payments, and returns."},
                *history[-4:],
                {"role":"user","content":msg}
            ],
            "max_tokens": 200, "temperature": 0.7
        }).encode()
        req = urllib.request.Request(
            'https://api.openai.com/v1/chat/completions',
            data=payload,
            headers={'Content-Type':'application/json','Authorization':f'Bearer {settings.OPENAI_API_KEY}'}
        )
        resp = json.loads(urllib.request.urlopen(req, timeout=8).read())
        return resp['choices'][0]['message']['content']
    except Exception:
        return "I'm having trouble right now. Please email support@shopai.com."


def chatbot_page(request):
    return render(request, 'chatbot/widget.html')


@csrf_exempt
def chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        msg = data.get('message','').strip()
        history = data.get('history', [])
        if not msg:
            return JsonResponse({'error': 'Empty message'}, status=400)
        reply = rule_response(msg) or order_lookup(msg, request.user) or product_search(msg) or openai_fallback(msg, history)
        return JsonResponse({'response': reply})
    except Exception as e:
        return JsonResponse({'response': 'Something went wrong. Please try again.'})
