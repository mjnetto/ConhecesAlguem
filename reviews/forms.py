from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Form for creating reviews"""
    rating = forms.IntegerField(
        widget=forms.HiddenInput(),
        min_value=1,
        max_value=5
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 5,
                'placeholder': 'Conte sua experiência com este profissional...'
            }),
        }
        labels = {
            'rating': 'Avaliação',
            'comment': 'Comentário (opcional)'
        }

