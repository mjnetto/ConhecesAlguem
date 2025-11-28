from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Client, Professional, PortfolioItem


class PortfolioItemInline(admin.TabularInline):
    model = PortfolioItem
    extra = 1
    fields = ['image', 'description', 'service_category']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'email', 'is_verified', 'booking_count', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['name', 'phone_number', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    def booking_count(self, obj):
        count = obj.bookings.count()
        if count > 0:
            url = reverse('admin:bookings_booking_changelist')
            return format_html('<a href="{}?client__id__exact={}">{} reservas</a>', url, obj.id, count)
        return '0 reservas'
    booking_count.short_description = 'Reservas'


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'phone_number', 
        'nif', 
        'is_activated', 
        'rating_display', 
        'booking_count',
        'created_at'
    ]
    list_filter = ['is_activated', 'created_at']
    search_fields = ['name', 'phone_number', 'nif', 'iban', 'email']
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'total_bookings', 
        'completed_bookings', 
        'average_rating',
        'activated_at'
    ]
    filter_horizontal = ['service_provinces', 'service_cities', 'service_neighborhoods']
    inlines = [PortfolioItemInline]
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('name', 'phone_number', 'email', 'profile_picture', 'bio')
        }),
        ('Modo de Contato', {
            'fields': ('contact_mode',),
            'description': 'Como os clientes podem entrar em contato: Agendamento via sistema ou Contato direto (telefone/WhatsApp)'
        }),
        ('Documentos', {
            'fields': ('nif', 'iban'),
            'description': 'NIF e IBAN são obrigatórios para ativação'
        }),
        ('Ativação', {
            'fields': (
                'is_activated', 
                'activated_at', 
                'activation_notes'
            ),
            'classes': ('wide',)
        }),
        ('Áreas de Serviço', {
            'fields': ('service_provinces', 'service_cities', 'service_neighborhoods'),
            'description': 'Selecione as áreas onde o profissional oferece serviços'
        }),
        ('Estatísticas', {
            'fields': (
                'total_bookings',
                'completed_bookings', 
                'average_rating'
            ),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_professionals', 'deactivate_professionals']
    
    def rating_display(self, obj):
        if obj.average_rating > 0:
            stars = '★' * int(obj.average_rating)
            return format_html(
                '<span style="color: gold;">{}</span> {} ({})',
                stars,
                f'{obj.average_rating:.1f}',
                obj.total_bookings
            )
        return 'Sem avaliações'
    rating_display.short_description = 'Avaliação'
    
    def booking_count(self, obj):
        count = obj.bookings.count()
        if count > 0:
            url = reverse('admin:bookings_booking_changelist')
            return format_html('<a href="{}?professional__id__exact={}">{} reservas</a>', url, obj.id, count)
        return '0 reservas'
    booking_count.short_description = 'Reservas'
    
    def activate_professionals(self, request, queryset):
        from django.utils import timezone
        from core.emails import send_professional_activation_email
        
        updated = 0
        for professional in queryset:
            if not professional.is_activated:
                professional.is_activated = True
                professional.activated_at = timezone.now()
                professional.save()
                # Send activation email
                send_professional_activation_email(professional)
                updated += 1
        
        self.message_user(request, f'{updated} profissionais ativados com sucesso.')
    activate_professionals.short_description = 'Ativar profissionais selecionados'
    
    def deactivate_professionals(self, request, queryset):
        updated = queryset.update(is_activated=False)
        self.message_user(request, f'{updated} profissionais desativados.')
    deactivate_professionals.short_description = 'Desativar profissionais selecionados'


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ['professional', 'service_category', 'created_at']
    list_filter = ['service_category', 'created_at']
    search_fields = ['professional__name', 'description']
