from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, Inventory
from .forms import ProductForm, InventoryForm, ProductSearchForm
from accounts.models import FarmerProfile
from .ai_recommendations import get_ai_recommendations_for_user, get_similar_products_ai

def product_list(request):
    products = Product.objects.filter(is_available=True).select_related('farmer', 'category')
    form = ProductSearchForm(request.GET)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        is_organic = form.cleaned_data.get('is_organic')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        
        if query:
            products = products.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(farmer__farm_name__icontains=query)
            )
        
        if category:
            products = products.filter(category=category)
        
        if is_organic:
            products = products.filter(is_organic=True)
        
        if min_price:
            products = products.filter(price__gte=min_price)
        
        if max_price:
            products = products.filter(price__lte=max_price)
    
    # AI Recommendations - THIS IS NEW
    ai_recommendations = []
    if request.user.is_authenticated and request.user.user_type == 'buyer':
        try:
            ai_recommendations = get_ai_recommendations_for_user(request.user, limit=6)
        except Exception as e:
            print(f"AI Recommendation Error: {e}")
            ai_recommendations = []

        # In product_list view, change this:
    # if request.user.is_authenticated and request.user.user_type == 'buyer':

    #     # To this (shows AI for everyone):
    #     if True:  # TEMPORARY - for testing
    #         # Create fake recommendations from available products
    #         products_for_ai = Product.objects.filter(is_available=True)[:6]
    #         ai_recommendations = [
    #             {
    #             'product': p,
    #             'reason': 'Recommended by our AI',
    #             'score': 1.0
    #             }
    #             for p in products_for_ai
    #     ]
    
    context = {
        'products': products,
        'form': form,
        'categories': Category.objects.all(),
        'ai_recommendations': ai_recommendations,  # ADD THIS LINE
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('farmer', 'category'), pk=pk)
    
    try:
        inventory = product.inventory
    except Inventory.DoesNotExist:
        inventory = None
    
    context = {
        'product': product,
        'inventory': inventory,
    }
    return render(request, 'products/product_detail.html', context)


@login_required
def product_create(request):
    if request.user.user_type != 'farmer':
        messages.error(request, 'Only farmers can add products.')
        return redirect('products:product_list')
    
    try:
        farmer_profile = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, 'Please complete your farmer profile first.')
        return redirect('accounts:profile_edit')
    
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        inventory_form = InventoryForm(request.POST)
        
        if product_form.is_valid() and inventory_form.is_valid():
            product = product_form.save(commit=False)
            product.farmer = farmer_profile
            product.save()
            
            inventory = inventory_form.save(commit=False)
            inventory.product = product
            inventory.save()
            
            messages.success(request, 'Product added successfully!')
            return redirect('products:farmer_products')
    else:
        product_form = ProductForm()
        inventory_form = InventoryForm()
    
    context = {
        'product_form': product_form,
        'inventory_form': inventory_form,
    }
    return render(request, 'products/product_form.html', context)


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if product.farmer.user != request.user:
        messages.error(request, 'You can only edit your own products.')
        return redirect('products:product_list')
    
    try:
        inventory = product.inventory
    except Inventory.DoesNotExist:
        inventory = None
    
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        inventory_form = InventoryForm(request.POST, instance=inventory)
        
        if product_form.is_valid() and inventory_form.is_valid():
            product_form.save()
            inventory_form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('products:farmer_products')
    else:
        product_form = ProductForm(instance=product)
        inventory_form = InventoryForm(instance=inventory)
    
    context = {
        'product_form': product_form,
        'inventory_form': inventory_form,
        'product': product,
        'editing': True,
    }
    return render(request, 'products/product_form.html', context)


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if product.farmer.user != request.user:
        messages.error(request, 'You can only delete your own products.')
        return redirect('products:product_list')
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('products:farmer_products')
    
    return render(request, 'products/product_confirm_delete.html', {'product': product})


@login_required
def farmer_products(request):
    if request.user.user_type != 'farmer':
        messages.error(request, 'Only farmers can access this page.')
        return redirect('products:product_list')
    
    try:
        farmer_profile = request.user.farmer_profile
        products = Product.objects.filter(farmer=farmer_profile).select_related('category')
        
        context = {
            'products': products,
            'farmer_profile': farmer_profile,
        }
        return render(request, 'products/farmer_products.html', context)
    except FarmerProfile.DoesNotExist:
        messages.error(request, 'Please complete your farmer profile first.')
        return redirect('accounts:profile_edit')


def search(request):
    form = ProductSearchForm(request.GET)
    products = Product.objects.filter(is_available=True)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            products = products.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(farmer__farm_name__icontains=query)
            )
    
    context = {
        'form': form,
        'products': products,
    }
    return render(request, 'products/search.html', context)

@login_required
def ai_recommendations(request):
    """Dedicated AI recommendations page"""
    if request.user.user_type != 'buyer':
        messages.error(request, 'This feature is available for buyers only.')
        return redirect('products:product_list')
    
    from .ai_recommendations import get_ai_recommendations_for_user
    
    try:
        recommendations = get_ai_recommendations_for_user(request.user, limit=12)
    except Exception as e:
        recommendations = []
        messages.warning(request, 'Could not generate AI recommendations at this time.')
    
    context = {
        'recommendations': recommendations,
    }
    return render(request, 'products/ai_recommendations.html', context)

