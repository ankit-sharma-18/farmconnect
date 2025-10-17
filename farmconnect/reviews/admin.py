from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'farmer', 'rating', 'quality_rating', 'communication_rating', 
                    'delivery_rating', 'would_recommend', 'created_at']
    list_filter = ['rating', 'would_recommend', 'created_at']
    search_fields = ['buyer__username', 'farmer__username', 'title', 'comment']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']