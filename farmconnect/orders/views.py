from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Order, Message, User
from .forms import OrderForm, OrderStatusForm, MessageForm
from products.models import Product

@login_required
def order_list(request):
    if request.user.user_type == 'farmer':
        orders = Order.objects.filter(product__farmer__user=request.user).select_related('buyer', 'product')
    else:
        orders = Order.objects.filter(buyer=request.user).select_related('product', 'product__farmer')
    
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    # Check permissions
    if order.buyer != request.user and order.product.farmer.user != request.user:
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('orders:order_list')
    
    # Handle status update for farmers
    if request.method == 'POST' and request.user == order.product.farmer.user:
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order status updated successfully!')
            return redirect('orders:order_detail', pk=pk)
    else:
        form = OrderStatusForm(instance=order)
    
    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def create_order(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    if request.user.user_type != 'buyer':
        messages.error(request, 'Only buyers can place orders.')
        return redirect('products:product_detail', pk=product_id)
    
    if not product.is_available:
        messages.error(request, 'This product is currently unavailable.')
        return redirect('products:product_detail', pk=product_id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.buyer = request.user
            order.product = product
            order.unit_price = product.price
            
            # Check inventory
            try:
                inventory = product.inventory
                if inventory.available_quantity >= order.quantity:
                    inventory.reserve(order.quantity)
                    order.save()
                    messages.success(request, 'Order placed successfully!')
                    return redirect('orders:order_detail', pk=order.pk)
                else:
                    messages.error(request, f'Insufficient stock. Only {inventory.available_quantity} {product.unit} available.')
            except:
                order.save()
                messages.success(request, 'Order placed successfully!')
                return redirect('orders:order_detail', pk=order.pk)
    else:
        form = OrderForm()
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'orders/create_order.html', context)


@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if order.buyer != request.user:
        messages.error(request, 'You can only cancel your own orders.')
        return redirect('orders:order_list')
    
    if order.status not in ['pending', 'confirmed']:
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('orders:order_detail', pk=pk)
    
    if request.method == 'POST':
        # Release inventory reservation
        try:
            inventory = order.product.inventory
            inventory.release_reservation(order.quantity)
        except:
            pass
        
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'Order cancelled successfully.')
        return redirect('orders:order_list')
    
    return render(request, 'orders/order_confirm_cancel.html', {'order': order})


@login_required
def messaging(request):
    sent_messages = Message.objects.filter(sender=request.user).select_related('recipient')
    received_messages = Message.objects.filter(recipient=request.user).select_related('sender')
    
    # Mark received messages as read when viewing
    unread_messages = received_messages.filter(is_read=False)
    unread_messages.update(is_read=True)
    
    context = {
        'sent_messages': sent_messages,
        'received_messages': received_messages,
    }
    return render(request, 'orders/messaging.html', context)


@login_required
def send_message(request, recipient_id=None, order_id=None):
    recipient = get_object_or_404(User, pk=recipient_id) if recipient_id else None
    order = get_object_or_404(Order, pk=order_id) if order_id else None
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            if recipient:
                message.recipient = recipient
            elif order:
                message.recipient = order.product.farmer.user if request.user == order.buyer else order.buyer
                message.order = order
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('orders:messaging')
    else:
        initial = {}
        if order:
            initial['subject'] = f'Regarding Order #{order.id}'
        form = MessageForm(initial=initial)
    
    context = {
        'form': form,
        'recipient': recipient,
        'order': order,
    }
    return render(request, 'orders/send_message.html', context)