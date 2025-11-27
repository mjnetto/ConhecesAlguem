from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Form for creating reviews"""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={
                'class': 'flex gap-4'
            }, choices=[(i, '★' * i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 5,
                'placeholder': 'Conte sua experiência com este profissional...'
            }),
        }
        labels = {
            'rating': 'Avaliação',
            'comment': 'Comentário (opcional)'
        }

