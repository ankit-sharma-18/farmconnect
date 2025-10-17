from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from orders.models import Order
from accounts.models import FarmerProfile

def review_list(request, farmer_id=None):
    if farmer_id:
        farmer_profile = get_object_or_404(FarmerProfile, pk=farmer_id)
        reviews = Review.objects.filter(farmer=farmer_profile.user).select_related('buyer', 'order')
        context = {
            'reviews': reviews,
            'farmer_profile': farmer_profile,
        }
    else:
        reviews = Review.objects.all().select_related('buyer', 'farmer', 'order')
        context = {
            'reviews': reviews,
        }
    
    return render(request, 'reviews/review_list.html', context)


@login_required
def create_review(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    # Check if buyer owns this order
    if order.buyer != request.user:
        messages.error(request, 'You can only review your own orders.')
        return redirect('orders:order_list')
    
    # Check if order is completed
    if order.status != 'completed':
        messages.error(request, 'You can only review completed orders.')
        return redirect('orders:order_detail', pk=order_id)
    
    # Check if review already exists
    if hasattr(order, 'review'):
        messages.info(request, 'You have already reviewed this order.')
        return redirect('reviews:review_list')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.buyer = request.user
            review.farmer = order.product.farmer.user
            review.order = order
            review.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('accounts:farmer_profile', pk=order.product.farmer.pk)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'order': order,
    }
    return render(request, 'reviews/review_form.html', context)


@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    
    if review.buyer != request.user:
        messages.error(request, 'You can only edit your own reviews.')
        return redirect('reviews:review_list')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully!')
            return redirect('reviews:review_list')
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
        'editing': True,
    }
    return render(request, 'reviews/review_form.html', context)


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    
    if review.buyer != request.user:
        messages.error(request, 'You can only delete your own reviews.')
        return redirect('reviews:review_list')
    
    if request.method == 'POST':
        farmer_profile = review.farmer.farmer_profile
        review.delete()
        farmer_profile.update_rating()
        messages.success(request, 'Review deleted successfully!')
        return redirect('reviews:review_list')
    
    return render(request, 'reviews/review_confirm_delete.html', {'review': review})