from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_radius = models.IntegerField(help_text="Delivery radius in kilometers", default=10)
    farm_image = models.ImageField(upload_to='farms/', blank=True, null=True)
    certification = models.CharField(max_length=200, blank=True, help_text="e.g., Organic, Non-GMO")
    established_year = models.IntegerField(null=True, blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.farm_name
    
    def update_rating(self):
        from reviews.models import Review
        reviews = Review.objects.filter(farmer=self.user)
        if reviews.exists():
            self.average_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.total_reviews = reviews.count()
            self.save()


class BuyerProfile(models.Model):
    BUYER_TYPE_CHOICES = (
        ('individual', 'Individual Consumer'),
        ('restaurant', 'Restaurant'),
        ('retailer', 'Retailer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    buyer_type = models.CharField(max_length=20, choices=BUYER_TYPE_CHOICES)
    business_name = models.CharField(max_length=200, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    preferred_delivery_time = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_buyer_type_display()}"


class AvailabilityCalendar(models.Model):
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    available = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text="Special notes for this day")
    
    class Meta:
        unique_together = ['farmer', 'date']
        ordering = ['date']
    
    def __str__(self):
        return f"{self.farmer.farm_name} - {self.date}"