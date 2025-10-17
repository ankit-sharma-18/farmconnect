from django import forms
from .models import Product, Category, Inventory

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'unit', 'image', 
                  'is_available', 'is_organic', 'harvest_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'harvest_date': forms.DateInput(attrs={'type': 'date'}),
            'price': forms.NumberInput(attrs={
                'placeholder': '₹ Enter price in Rupees',  # ADDED
                'step': '0.01',
                'min': '0'
            })
        }
        labels = {
            'price': 'Price in Rupees (₹)',  # ADDED
        }
        help_texts = {
            'price': 'Enter the price in Indian Rupees (₹)',  # ADDED
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'is_available' and field != 'is_organic':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-check-input'})


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['quantity', 'low_stock_threshold']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class ProductSearchForm(forms.Form):
    query = forms.CharField(max_length=200, required=False, 
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                               'placeholder': 'Search products...'
                           }))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), 
                                     required=False,
                                     widget=forms.Select(attrs={'class': 'form-select'}))
    is_organic = forms.BooleanField(required=False, 
                                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    min_price = forms.DecimalField(required=False, min_value=0,
                                   widget=forms.NumberInput(attrs={
                                       'class': 'form-control',
                                       'placeholder': 'Min price'
                                   }))
    max_price = forms.DecimalField(required=False, min_value=0,
                                   widget=forms.NumberInput(attrs={
                                       'class': 'form-control',
                                       'placeholder': 'Max price'
                                   }))