from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from .forms import UserRegistrationForm, UserLoginForm, FarmerProfileForm, BuyerProfileForm
from .models import User, FarmerProfile, BuyerProfile
from products.models import Product
from orders.models import Order

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Please complete your profile.')
            return redirect('accounts:profile_edit')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('accounts:dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def dashboard(request):
    context = {}
    
    if request.user.user_type == 'farmer':
        try:
            farmer_profile = request.user.farmer_profile
            products = Product.objects.filter(farmer=farmer_profile)
            orders = Order.objects.filter(product__farmer=farmer_profile)
            
            context.update({
                'profile': farmer_profile,
                'products': products,
                'total_products': products.count(),
                'total_orders': orders.count(),
                'pending_orders': orders.filter(status='pending').count(),
                'total_revenue': orders.filter(status='completed').aggregate(
                    total=Sum('total_price'))['total'] or 0,
                'recent_orders': orders.order_by('-created_at')[:5],
            })
        except FarmerProfile.DoesNotExist:
            messages.warning(request, 'Please complete your farmer profile.')
            return redirect('accounts:profile_edit')
    
    elif request.user.user_type == 'buyer':
        try:
            buyer_profile = request.user.buyer_profile
            orders = Order.objects.filter(buyer=request.user)
            
            context.update({
                'profile': buyer_profile,
                'total_orders': orders.count(),
                'pending_orders': orders.filter(status='pending').count(),
                'completed_orders': orders.filter(status='completed').count(),
                'recent_orders': orders.order_by('-created_at')[:5],
            })
        except BuyerProfile.DoesNotExist:
            messages.warning(request, 'Please complete your buyer profile.')
            return redirect('accounts:profile_edit')
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_edit(request):
    if request.user.user_type == 'farmer':
        try:
            profile = request.user.farmer_profile
        except FarmerProfile.DoesNotExist:
            profile = None
        
        if request.method == 'POST':
            form = FarmerProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                messages.success(request, 'Farmer profile updated successfully!')
                return redirect('accounts:dashboard')
        else:
            form = FarmerProfileForm(instance=profile)
        
        return render(request, 'accounts/profile_edit.html', {'form': form, 'profile_type': 'farmer'})
    
    elif request.user.user_type == 'buyer':
        try:
            profile = request.user.buyer_profile
        except BuyerProfile.DoesNotExist:
            profile = None
        
        if request.method == 'POST':
            form = BuyerProfileForm(request.POST, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                messages.success(request, 'Buyer profile updated successfully!')
                return redirect('accounts:dashboard')
        else:
            form = BuyerProfileForm(instance=profile)
        
        return render(request, 'accounts/profile_edit.html', {'form': form, 'profile_type': 'buyer'})


def farmer_profile_view(request, pk):
    farmer_profile = get_object_or_404(FarmerProfile, pk=pk)
    products = Product.objects.filter(farmer=farmer_profile, is_available=True)
    
    context = {
        'farmer': farmer_profile,
        'products': products,
    }
    return render(request, 'accounts/farmer_profile.html', context)


def buyer_profile_view(request, pk):
    buyer_profile = get_object_or_404(BuyerProfile, pk=pk)
    
    context = {
        'buyer': buyer_profile,
    }
    return render(request, 'accounts/buyer_profile.html', context)