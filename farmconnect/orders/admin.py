from django.contrib import admin
from .models import Order, Message

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'product', 'quantity', 'total_price', 'status', 'delivery_method', 'created_at']
    list_filter = ['status', 'delivery_method', 'created_at']
    search_fields = ['buyer__username', 'product__name']
    date_hierarchy = 'created_at'
    readonly_fields = ['total_price', 'unit_price']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'subject', 'content']
    date_hierarchy = 'created_at'