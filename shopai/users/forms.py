from django import forms
from django.contrib.auth import get_user_model
from .models import Address

User = get_user_model()

WIDGET = lambda placeholder: forms.TextInput(attrs={'class':'form-control','placeholder':placeholder})
EMAIL_W = lambda p: forms.EmailInput(attrs={'class':'form-control','placeholder':p})
PASS_W = lambda p: forms.PasswordInput(attrs={'class':'form-control','placeholder':p})

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=PASS_W('Password'), label='Password')
    password2 = forms.CharField(widget=PASS_W('Confirm Password'), label='Confirm Password')

    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','phone']
        widgets = {
            'username': WIDGET('Username'),
            'email': EMAIL_W('Email'),
            'first_name': WIDGET('First Name'),
            'last_name': WIDGET('Last Name'),
            'phone': WIDGET('Phone Number'),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match.")
        return cleaned


class LoginForm(forms.Form):
    email = forms.EmailField(widget=EMAIL_W('Email'))
    password = forms.CharField(widget=PASS_W('Password'))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','phone','date_of_birth']
        widgets = {
            'first_name': WIDGET('First Name'),
            'last_name': WIDGET('Last Name'),
            'phone': WIDGET('Phone'),
            'date_of_birth': forms.DateInput(attrs={'class':'form-control','type':'date'}),
        }


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['user','created_at']
        widgets = {f: forms.TextInput(attrs={'class':'form-control'}) for f in
                   ['full_name','phone','address_line1','address_line2','city','state','pincode','country']}


class OTPForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter 6-digit OTP',
                                       'style':'letter-spacing:8px;font-size:1.5rem;text-align:center;'}))
