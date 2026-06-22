import random, string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Address, OTPRecord
from .forms import RegisterForm, LoginForm, ProfileForm, AddressForm, OTPForm

User = get_user_model()

def gen_otp():
    return ''.join(random.choices(string.digits, k=6))


def register_view(request):
    if request.user.is_authenticated:
        return redirect('store:index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.is_active = True
            user.save()
            code = gen_otp()
            OTPRecord.objects.create(user=user, otp_type='email', code=code,
                                     expires_at=timezone.now()+timedelta(minutes=10))
            print(f"[DEV] OTP for {user.email}: {code}")  # shown in console
            messages.success(request, f'Account created! Your OTP is: {code} (check console in dev)')
            return redirect('users:verify_otp', user_id=user.id)
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def verify_otp(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = OTPRecord.objects.filter(user=user, code=form.cleaned_data['code'],
                                           is_used=False, otp_type='email').first()
            if otp and otp.is_valid:
                otp.is_used = True
                otp.save()
                user.is_email_verified = True
                user.save()
                login(request, user)
                messages.success(request, 'Email verified! Welcome to ShopAI!')
                return redirect('store:index')
            messages.error(request, 'Invalid or expired OTP.')
    else:
        form = OTPForm()
    return render(request, 'users/verify_otp.html', {'form': form, 'user_obj': user})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:index')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['email'],
                                password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect(request.GET.get('next', '/'))
            messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('store:index')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form,
                  'addresses': request.user.addresses.all()})


@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.user = request.user
            addr.save()
            messages.success(request, 'Address added!')
            return redirect('users:profile')
    else:
        form = AddressForm()
    return render(request, 'users/address_form.html', {'form': form})


@login_required
def delete_address(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    addr.delete()
    messages.success(request, 'Address deleted.')
    return redirect('users:profile')


@login_required
def toggle_dark_mode(request):
    request.user.dark_mode = not request.user.dark_mode
    request.user.save(update_fields=['dark_mode'])
    return JsonResponse({'dark_mode': request.user.dark_mode})
