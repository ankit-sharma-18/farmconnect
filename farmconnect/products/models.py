from django.db import models
from accounts.models import FarmerProfile
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = (
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('lb', 'Pound'),
        ('oz', 'Ounce'),
        ('piece', 'Piece'),
        ('dozen', 'Dozen'),
        ('bunch', 'Bunch'),
        ('bag', 'Bag'),
    )
    
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text="Price in Indian Rupees (₹)"  # UPDATED
    )
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_organic = models.BooleanField(default=False)
    harvest_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - ₹{self.price}/{self.unit}"

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    reserved_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    low_stock_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    last_restocked = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Inventories'
    
    def __str__(self):
        return f"{self.product.name} - {self.available_quantity} available"
    
    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity
    
    @property
    def is_low_stock(self):
        return self.available_quantity <= self.low_stock_threshold
    
    def reserve(self, amount):
        if self.available_quantity >= amount:
            self.reserved_quantity += amount
            self.save()
            return True
        return False
    
    def release_reservation(self, amount):
        self.reserved_quantity -= amount
        if self.reserved_quantity < 0:
            self.reserved_quantity = 0
        self.save()
    
    def complete_sale(self, amount):
        self.quantity -= amount
        self.reserved_quantity -= amount
        if self.quantity < 0:
            self.quantity = 0
        if self.reserved_quantity < 0:
            self.reserved_quantity = 0
        self.save()