from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import FarmerProfile
from orders.models import Order
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Review(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review', null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    quality_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    delivery_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    would_recommend = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['buyer', 'order']
    
    def __str__(self):
        return f"{self.buyer.username} - {self.farmer.username} - {self.rating} stars"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update farmer's average rating
        try:
            farmer_profile = self.farmer.farmer_profile
            farmer_profile.update_rating()
        except:
            pass