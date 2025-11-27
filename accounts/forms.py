from django import forms
from phonenumber_field.formfields import PhoneNumberField
from .models import Professional, PortfolioItem
from locations.models import Province, City
from services.models import ServiceCategory


class ProfessionalRegistrationStep1Form(forms.ModelForm):
    """Step 1: Basic Information"""
    phone_number = PhoneNumberField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': '+244 912 345 678'
        }),
        help_text="Formato: +244 912 345 678"
    )
    
    class Meta:
        model = Professional
        fields = ['name', 'phone_number', 'email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Seu nome completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'seu@email.com (opcional)'
            }),
        }


class ProfessionalRegistrationStep2Form(forms.ModelForm):
    """Step 2: Documents and Profile"""
    class Meta:
        model = Professional
        fields = ['nif', 'iban', 'profile_picture', 'bio']
        widgets = {
            'nif': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ex: 123456789LA045'
            }),
            'iban': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ex: AO06004400012345678910144'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Conte-nos sobre sua experiência e especialidades...'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'accept': 'image/*'
            }),
        }


class ProfessionalRegistrationStep3Form(forms.Form):
    """Step 3: Service Categories and Areas"""
    service_categories = forms.ModelMultipleChoiceField(
        queryset=ServiceCategory.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2'
        }),
        required=True,
        help_text="Selecione pelo menos uma categoria de serviço que você oferece"
    )
    
    service_provinces = forms.ModelMultipleChoiceField(
        queryset=Province.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2'
        }),
        required=True,
        help_text="Selecione as províncias onde você trabalha"
    )
    
    service_cities = forms.ModelMultipleChoiceField(
        queryset=City.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2'
        }),
        required=False,
        help_text="Selecione as cidades específicas (opcional)"
    )


class PortfolioItemForm(forms.ModelForm):
    """Form for portfolio items"""
    class Meta:
        model = PortfolioItem
        fields = ['image', 'description']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'accept': 'image/*'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Descreva este trabalho...'
            }),
        }

