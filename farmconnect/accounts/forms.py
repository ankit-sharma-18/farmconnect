from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, FarmerProfile, BuyerProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'user_type', 'phone', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})


class FarmerProfileForm(forms.ModelForm):
    class Meta:
        model = FarmerProfile
        fields = [
            'farm_name', 'description', 'address', 'city', 'state', 'zip_code',
            'latitude', 'longitude', 'delivery_radius', 'farm_image',
            'certification', 'established_year'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class BuyerProfileForm(forms.ModelForm):
    class Meta:
        model = BuyerProfile
        fields = [
            'buyer_type', 'business_name', 'address', 'city', 'state', 'zip_code',
            'latitude', 'longitude', 'preferred_delivery_time'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})