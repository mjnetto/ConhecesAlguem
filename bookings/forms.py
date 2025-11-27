from django import forms
from django.core.exceptions import ValidationError
from datetime import date, datetime, time
from phonenumber_field.formfields import PhoneNumberField


class BookingConfirmForm(forms.Form):
    """Form for confirming a booking"""
    client_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Seu nome completo'
        }),
        label='Nome',
        required=True
    )
    
    phone_number = PhoneNumberField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': '+244 912 345 678'
        }),
        label='Telefone',
        required=True,
        help_text="Formato: +244 912 345 678"
    )
    
    scheduled_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'type': 'date'
        }),
        label='Data',
        required=True
    )
    
    scheduled_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'type': 'time'
        }),
        label='Hora',
        required=True
    )
    
    special_instructions = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'rows': 4,
            'placeholder': 'Instruções especiais ou detalhes adicionais...'
        }),
        label='Instruções Especiais',
        required=False,
        max_length=1000
    )
    
    def clean_client_name(self):
        name = self.cleaned_data.get('client_name', '').strip()
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
    
    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date:
            # Don't allow past dates
            if scheduled_date < date.today():
                raise ValidationError('A data não pode ser no passado. Por favor, selecione uma data futura.')
            
            # Don't allow dates too far in the future (max 6 months)
            from datetime import timedelta
            max_date = date.today() + timedelta(days=180)
            if scheduled_date > max_date:
                raise ValidationError('A data não pode ser mais de 6 meses no futuro.')
        
        return scheduled_date
    
    def clean_scheduled_time(self):
        scheduled_time = self.cleaned_data.get('scheduled_time')
        scheduled_date = self.cleaned_data.get('scheduled_date')
        
        if scheduled_time and scheduled_date:
            # If the date is today, don't allow past times
            if scheduled_date == date.today():
                current_time = datetime.now().time()
                if scheduled_time < current_time:
                    raise ValidationError('A hora não pode ser no passado para reservas de hoje.')
            
            # Business hours validation (optional - can be adjusted)
            # Allow bookings between 6 AM and 10 PM
            min_time = time(6, 0)
            max_time = time(22, 0)
            if scheduled_time < min_time or scheduled_time > max_time:
                raise ValidationError('As reservas devem ser agendadas entre 6h00 e 22h00.')
        
        return scheduled_time
    
    def clean_special_instructions(self):
        instructions = self.cleaned_data.get('special_instructions', '').strip()
        if instructions and len(instructions) > 1000:
            raise ValidationError('As instruções especiais não podem ter mais de 1000 caracteres.')
        return instructions


