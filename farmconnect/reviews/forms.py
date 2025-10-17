from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'quality_rating', 
                  'communication_rating', 'delivery_rating', 'would_recommend']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'quality_rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'communication_rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'delivery_rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'would_recommend':
                if isinstance(self.fields[field].widget, forms.Textarea):
                    self.fields[field].widget.attrs.update({'class': 'form-control'})
                elif isinstance(self.fields[field].widget, forms.Select):
                    self.fields[field].widget.attrs.update({'class': 'form-select'})
                else:
                    self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-check-input'})