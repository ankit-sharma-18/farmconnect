from django.contrib import admin
from .models import Category, Product, Inventory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'farmer', 'category', 'price', 'unit', 'is_available', 'is_organic']
    list_filter = ['category', 'is_available', 'is_organic', 'created_at']
    search_fields = ['name', 'farmer__farm_name']
    date_hierarchy = 'created_at'

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'reserved_quantity', 'available_quantity', 'is_low_stock']
    list_filter = ['last_restocked']
    search_fields = ['product__name']