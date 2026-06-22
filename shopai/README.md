# 🛍️ ShopAI — Full-Stack AI E-Commerce Platform

Django-based e-commerce platform with all 20 features: AI recommendations, real-time order tracking, payment gateways, AI chatbot, multi-vendor marketplace, analytics dashboard, and more.

**This project has been tested end-to-end — every page, every flow (registration → OTP → cart → checkout → order tracking → admin analytics) renders and works correctly out of the box.**
**My GitHub Account - https://github.com/Ganeshgawade9**
**My Linkedin Profile - https://www.linkedin.com/in/ganeshgawade90/**
---

## ✅ Requirements

- Python 3.10, 3.11, or 3.12 (NOT 3.13 — some packages don't have wheels yet)
- pip
- 5 minutes of your time

---

## 🚀 Setup — Exact Commands (copy-paste, in order)

### Windows (Command Prompt / PowerShell)

```bat
cd shopai

REM 1. Create virtual environment
python -m venv venv

REM 2. Activate it
venv\Scripts\activate

REM 3. Install dependencies
pip install -r requirements.txt

REM 4. Create database tables
python manage.py migrate

REM 5. Seed demo data (superuser + sample products)
python manage.py seed_data

REM 6. Run the server
python manage.py runserver
```

### macOS / Linux

```bash
cd shopai

# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create database tables
python manage.py migrate

# 5. Seed demo data (superuser + sample products)
python manage.py seed_data

# 6. Run the server
python manage.py runserver
```

### Then open your browser

| Page | URL |
|---|---|
| Homepage (storefront) | http://127.0.0.1:8000/ |
| Django Admin | http://127.0.0.1:8000/admin/ |
| Analytics Dashboard | http://127.0.0.1:8000/analytics/dashboard/ |
| REST API (products) | http://127.0.0.1:8000/api/v1/products/ |

**Admin login:** `admin@shopai.com` / `admin123`

---

## 🔑 If `pip install` fails

If you see errors about `numpy`/`scipy`/`scikit-learn` wheels, it's almost always a Python version issue. Run:

```bash
python --version
```

If it shows `3.13.x`, install Python 3.11 or 3.12 instead and recreate the venv with that version (e.g. `python3.11 -m venv venv`).

If you see `pkg_resources` errors, run:
```bash
pip install --upgrade setuptools
```
(already included in requirements.txt, but some systems need it installed first)

---

## 📂 Project Structure

```
shopai/
├── shopai/              Django project config (settings.py, urls.py, wsgi.py)
├── store/               Products, categories, brands, AI recommendation engine
│   └── management/commands/seed_data.py    ← demo data seeder
├── users/               Custom user model, OTP verification, addresses
├── orders/               Orders, 5-step tracking, Razorpay/Stripe/COD payment
├── cart/                 Shopping cart (AJAX add/remove/update)
├── wishlist/             Wishlist (toggle + move-to-cart)
├── reviews/               Star ratings, text reviews, photo uploads
├── chatbot/               AI chatbot (rule-based + OpenAI fallback)
├── vendor/                 Multi-vendor marketplace (seller registration + dashboard)
├── analytics/             Admin analytics dashboard (Chart.js: revenue, orders, top products)
├── notifications/         Email notification service (console backend in dev)
├── api/                   Django REST Framework + JWT auth (mobile-ready API)
├── templates/            All HTML templates (base.html + per-app folders)
├── static/                CSS/JS/images
├── media/                  User-uploaded files (product images, avatars, reviews)
├── manage.py
├── requirements.txt
└── .env.example           Optional real API keys (Razorpay/Stripe/Twilio/OpenAI)
```

---

## ✅ All 20 Features — Where to Find Them

| # | Feature | Location | How to See It |
|---|---------|----------|----------------|
| 1 | AI Product Recommendations (cosine similarity) | `store/recommendation.py` | Log in, browse a few products, revisit homepage → "Recommended for You" |
| 2 | Real-Time Order Tracking (5-step progress bar) | `orders/` | Place an order → Order Detail page |
| 3 | Smart Search + Filters | `store/views.py`, `/products/` | Use sidebar filters: category, price, brand, rating, stock |
| 4 | Payment Integration (Razorpay/Stripe/COD) | `orders/views.py` | Checkout page → choose payment method |
| 5 | Admin Analytics Dashboard | `analytics/` | `/analytics/dashboard/` (staff login required) |
| 6 | Wishlist System | `wishlist/` | Heart icon on any product card |
| 7 | Product Review & Rating + Photos | `reviews/` | Product detail page → Reviews tab |
| 8 | Email & SMS Notifications | `notifications/email_service.py` | Console output on order placement (dev mode) |
| 9 | AI Chatbot | `chatbot/` | Chat bubble bottom-right corner, every page |
| 10 | Multi-Vendor Marketplace | `vendor/` | `/vendor/register/` → become a seller |
| 11 | Dark Mode Toggle | `base.html` | Moon/sun icon in navbar |
| 12 | Responsive Mobile Design | All templates | Resize browser / open on phone |
| 13 | Animated Product Cards | CSS in `base.html` | Hover over any product card |
| 14 | JWT Authentication | `api/` | `POST /api/v1/auth/login/` |
| 15 | OTP Verification | `users/` | Register a new account → OTP printed to server console |
| 16 | CAPTCHA-ready forms | `users/forms.py` | (django-simple-captcha can be added; forms are structured for it) |
| 17 | Inventory Management | `store/models.py` | Stock auto-deducts on order; low-stock badge shows on product cards |
| 18 | REST API for Mobile Apps | `api/` | `/api/v1/products/`, `/api/v1/orders/`, etc. |
| 19 | AI Price Prediction | `store/recommendation.py` → `predict_discount()` | Shown on product detail page as "AI Insight" |
| 20 | Personalized Homepage | `store/views.py` → `index()` | Recommendations + Recently Viewed sections |

---

## 🔌 REST API Reference

Base URL: `http://127.0.0.1:8000/api/v1/`

```
Auth
  POST   /auth/register/          { "email", "password", "username" }
  POST   /auth/login/             { "email", "password" } → { access, refresh }
  POST   /auth/token/refresh/     { "refresh" } → { access }
  GET    /auth/profile/           (requires Bearer token)

Products
  GET    /products/                List (filter by ?category=, ?brand=, ?is_featured=, ?is_trending=)
  GET    /products/{id}/           Detail
  GET    /products/featured/       Featured only
  GET    /products/trending/       Trending only
  GET    /products/{id}/similar/   AI-similar products

Categories
  GET    /categories/

Orders (auth required)
  GET    /orders/
  GET    /orders/{id}/

Cart (auth required)
  GET    /cart/
  POST   /cart/                   { "product_id", "quantity" }

AI
  GET    /recommendations/        (auth required) AI-personalized picks
```

Example login with `curl`:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@shopai.com","password":"admin123"}'
```

---

## 💳 Going Live with Real Payments (optional)

The project runs perfectly with **Cash on Delivery** with zero configuration. To enable real Razorpay/Stripe payments:

1. Copy `.env.example` to `.env`
2. Fill in your real API keys (get them from Razorpay/Stripe dashboards)
3. Install `python-dotenv` is already in requirements — but you also need to load it. Add this to the top of `shopai/settings.py` if not already there:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```
4. Restart the server

Without these keys, selecting Razorpay/Stripe at checkout will gracefully fall back to COD with a warning message (no crash).

---

## 📧 Email Notifications

By default, emails print to your **terminal/console** (Django's console email backend) — this is intentional for development so you can see OTPs and order confirmations without setting up a mail server.

To send real emails, edit `shopai/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-gmail-app-password'  # Generate from Google Account → Security → App Passwords
```

---

## 🤖 AI Chatbot

Works immediately with **zero configuration** using a built-in rule-based engine that handles:
- Greetings, order tracking (by order number), shipping/returns/payment FAQs, product search, vendor info

To add OpenAI GPT fallback for questions it doesn't recognize, set `OPENAI_API_KEY` in `.env` or as an environment variable.

---

## 🏪 Adding More Products

1. Go to `http://127.0.0.1:8000/admin/`
2. Login with `admin@shopai.com` / `admin123`
3. Click **Store → Products → Add Product**
4. Upload images, set price/stock/category, mark Featured/Trending

Or run `python manage.py seed_data` again any time to re-check/add the demo catalog.

---

## 🧑‍💻 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2.7 |
| API | Django REST Framework + SimpleJWT |
| Database | SQLite (zero-config, swap to PostgreSQL for production) |
| AI/ML | scikit-learn (cosine similarity recommendation engine) |
| Payments | Razorpay, Stripe, Cash on Delivery |
| SMS | Twilio (optional) |
| Email | Django console backend (dev) / SMTP (production) |
| Chatbot | Rule-based engine + OpenAI GPT-3.5 fallback |
| Frontend | Bootstrap 5, vanilla JS, custom CSS design system |
| Charts | Chart.js |
| Auth | Session-based (web) + JWT (API/mobile) |

---

## 🔒 Before Deploying to Production

- [ ] Change `SECRET_KEY` in `shopai/settings.py`
- [ ] Set `DEBUG = False`
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Switch to PostgreSQL (`pip install psycopg2-binary`, update `DATABASES`)
- [ ] Configure real SMTP email backend
- [ ] Add real Razorpay/Stripe keys
- [ ] Run `python manage.py collectstatic`
- [ ] Use a production server (gunicorn + nginx) instead of `runserver`

---

Built as an MCA Final Year Project — JSPM University, Pune 🎓
