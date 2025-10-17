from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FarmerProfile, BuyerProfile, AvailabilityCalendar

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'user_type', 'is_staff']
    list_filter = ['user_type', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('user_type', 'phone', 'profile_image')}),
    )

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ['farm_name', 'user', 'city', 'state', 'average_rating', 'total_reviews']
    list_filter = ['city', 'state', 'certification']
    search_fields = ['farm_name', 'user__username', 'city']

@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'buyer_type', 'business_name', 'city', 'state']
    list_filter = ['buyer_type', 'city', 'state']
    search_fields = ['user__username', 'business_name', 'city']

@admin.register(AvailabilityCalendar)
class AvailabilityCalendarAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'date', 'available']
    list_filter = ['available', 'date']
    date_hierarchy = 'date'