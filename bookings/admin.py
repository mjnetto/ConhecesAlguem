from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'client_link', 
        'professional_link',
        'service_category',
        'status_badge',
        'scheduled_date',
        'created_at'
    ]
    list_filter = ['status', 'scheduled_date', 'created_at', 'province']
    search_fields = [
        'client__name', 
        'client__phone_number',
        'professional__name', 
        'professional__phone_number',
        'service_description',
        'address_line'
    ]
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Partes Envolvidas', {
            'fields': ('client', 'professional', 'service')
        }),
        ('Localização', {
            'fields': ('province', 'city', 'neighborhood', 'address_line')
        }),
        ('Detalhes do Serviço', {
            'fields': ('service_description', 'special_instructions')
        }),
        ('Agendamento', {
            'fields': ('scheduled_date', 'scheduled_time')
        }),
        ('Status e Pagamento', {
            'fields': ('status', 'agreed_price')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'mark_cancelled', 'mark_confirmed']
    
    def client_link(self, obj):
        url = reverse('admin:accounts_client_change', args=[obj.client.id])
        return format_html('<a href="{}">{}</a>', url, obj.client.name)
    client_link.short_description = 'Cliente'
    
    def professional_link(self, obj):
        url = reverse('admin:accounts_professional_change', args=[obj.professional.id])
        return format_html('<a href="{}">{}</a>', url, obj.professional.name)
    professional_link.short_description = 'Profissional'
    
    def service_category(self, obj):
        return obj.service.category.name
    service_category.short_description = 'Categoria'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'confirmed': '#17a2b8',
            'in_progress': '#007bff',
            'completed': '#28a745',
            'cancelled': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def mark_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f'{updated} reservas marcadas como concluídas.')
    mark_completed.short_description = 'Marcar como concluído'
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} reservas canceladas.')
    mark_cancelled.short_description = 'Cancelar reservas'
    
    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} reservas confirmadas.')
    mark_confirmed.short_description = 'Confirmar reservas'
