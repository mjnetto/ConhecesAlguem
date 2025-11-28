from django import forms
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from .models import Professional, PortfolioItem, Report
from locations.models import Province, City
from services.models import ServiceCategory
import re


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
    
    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 3:
            raise ValidationError('O nome deve ter pelo menos 3 caracteres.')
        if len(name) > 200:
            raise ValidationError('O nome não pode ter mais de 200 caracteres.')
        return name
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Check if it's an Angola number
            if phone_number.country_code != 244:
                raise ValidationError('Por favor, use um número de telefone de Angola (+244).')
        return phone_number


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
                'placeholder': 'Ex: AO06004400012345678910144 (opcional)'
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
    
    def clean_nif(self):
        nif = self.cleaned_data.get('nif', '').strip().upper()
        if not nif:
            raise ValidationError('O NIF é obrigatório.')
        
        # Basic format validation (Angola NIF format: numbers + letters, usually ends with LA)
        if len(nif) < 9 or len(nif) > 20:
            raise ValidationError('O NIF deve ter entre 9 e 20 caracteres.')
        
        # Allow alphanumeric characters
        if not re.match(r'^[A-Z0-9]+$', nif):
            raise ValidationError('O NIF deve conter apenas letras e números.')
        
        return nif
    
    def clean_iban(self):
        iban = self.cleaned_data.get('iban', '').strip().upper().replace(' ', '')
        # IBAN é opcional
        if not iban:
            return ''  # Retorna string vazia se não fornecido
        
        # Angola IBAN format: AO + 23 digits = 25 characters total
        if not iban.startswith('AO'):
            raise ValidationError('O IBAN deve começar com "AO" (código de Angola).')
        
        if len(iban) != 25:
            raise ValidationError('O IBAN de Angola deve ter exatamente 25 caracteres (AO + 23 dígitos).')
        
        # Check if after "AO" there are only digits
        if not iban[2:].isdigit():
            raise ValidationError('Após "AO", o IBAN deve conter apenas números.')
        
        return iban
    
    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            # Check file size (max 5MB)
            if picture.size > 5 * 1024 * 1024:
                raise ValidationError('A imagem deve ter no máximo 5MB.')
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if picture.content_type not in allowed_types:
                raise ValidationError('Por favor, envie uma imagem nos formatos JPG, PNG ou GIF.')
        
        return picture
    
    def clean_bio(self):
        bio = self.cleaned_data.get('bio', '').strip()
        if bio and len(bio) > 1000:
            raise ValidationError('A biografia não pode ter mais de 1000 caracteres.')
        return bio


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
    
    def clean_service_categories(self):
        categories = self.cleaned_data.get('service_categories')
        if not categories or len(categories) == 0:
            raise ValidationError('Você deve selecionar pelo menos uma categoria de serviço.')
        if len(categories) > 10:
            raise ValidationError('Você não pode selecionar mais de 10 categorias.')
        return categories
    
    def clean_service_provinces(self):
        provinces = self.cleaned_data.get('service_provinces')
        if not provinces or len(provinces) == 0:
            raise ValidationError('Você deve selecionar pelo menos uma província onde trabalha.')
        return provinces


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
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('A imagem deve ter no máximo 5MB.')
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if image.content_type not in allowed_types:
                raise ValidationError('Por favor, envie uma imagem nos formatos JPG, PNG ou GIF.')
        return image


class ReportForm(forms.ModelForm):
    """Form for reporting professionals or clients"""
    
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'rows': 5,
                'placeholder': 'Descreva em detalhes o problema que você encontrou...'
            }),
        }
        labels = {
            'reason': 'Motivo da Denúncia',
            'description': 'Descrição do Problema',
        }
        help_texts = {
            'description': 'Forneça detalhes específicos sobre o problema. Quanto mais informações, melhor poderemos investigar.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].empty_label = None
        self.fields['description'].required = True
        
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 20:
            raise forms.ValidationError('Por favor, forneça uma descrição mais detalhada (mínimo 20 caracteres).')
        return description
