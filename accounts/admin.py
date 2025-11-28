from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Client, Professional, PortfolioItem, ProfileView, Report


class PortfolioItemInline(admin.TabularInline):
    model = PortfolioItem
    extra = 1
    fields = ['image', 'description', 'service_category']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'email', 'is_verified', 'is_blocked', 'report_count', 'booking_count', 'created_at']
    list_filter = ['is_verified', 'is_blocked', 'created_at']
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
        'is_blocked',
        'rating_display', 
        'booking_count',
        'report_count',
        'created_at'
    ]
    list_filter = ['is_activated', 'is_blocked', 'created_at']
    search_fields = ['name', 'phone_number', 'nif', 'iban', 'email']
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'total_bookings', 
        'completed_bookings', 
        'average_rating',
        'activated_at',
        'last_seen',
        'report_count'
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
                'average_rating',
                'report_count'
            ),
            'classes': ('collapse',)
        }),
        ('Sistema de Denúncias', {
            'fields': ('is_blocked',),
            'description': 'Usuários bloqueados não aparecem nos resultados de busca'
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


@admin.register(ProfileView)
class ProfileViewAdmin(admin.ModelAdmin):
    list_display = ['professional', 'ip_address', 'created_at']
    list_filter = ['created_at', 'professional']
    search_fields = ['professional__name', 'ip_address']
    readonly_fields = ['professional', 'ip_address', 'user_agent', 'created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False  # Views são criadas automaticamente


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'get_reported',
        'get_reporter',
        'reason_display',
        'status',
        'created_at',
        'action_buttons'
    ]
    list_filter = ['status', 'reason', 'created_at']
    search_fields = [
        'reported_professional__name',
        'reported_client__name',
        'reporter_client__name',
        'reporter_professional__name',
        'description'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informações da Denúncia', {
            'fields': (
                ('reporter_client', 'reporter_professional'),
                ('reported_professional', 'reported_client'),
                'reason',
                'description',
            )
        }),
        ('Status e Análise', {
            'fields': ('status', 'admin_notes', 'resolved_at'),
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_resolved', 'mark_dismissed', 'block_reported_user']
    
    def get_reported(self, obj):
        reported = obj.reported_professional or obj.reported_client
        if obj.reported_professional:
            return format_html(
                '<a href="{}">Profissional: {}</a>',
                reverse('admin:accounts_professional_change', args=[obj.reported_professional.id]),
                reported
            )
        return format_html(
            '<a href="{}">Cliente: {}</a>',
            reverse('admin:accounts_client_change', args=[obj.reported_client.id]),
            reported
        )
    get_reported.short_description = 'Denunciado'
    
    def get_reporter(self, obj):
        reporter = obj.reporter_client or obj.reporter_professional
        if obj.reporter_client:
            return format_html(
                '<a href="{}">Cliente: {}</a>',
                reverse('admin:accounts_client_change', args=[obj.reporter_client.id]),
                reporter
            )
        if obj.reporter_professional:
            return format_html(
                '<a href="{}">Profissional: {}</a>',
                reverse('admin:accounts_professional_change', args=[obj.reporter_professional.id]),
                reporter
            )
        return 'Anônimo'
    get_reporter.short_description = 'Denunciante'
    
    def reason_display(self, obj):
        return obj.get_reason_display()
    reason_display.short_description = 'Motivo'
    
    def action_buttons(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a href="{}?report_id={}&action=resolve" class="button">Resolver</a> | '
                '<a href="{}?report_id={}&action=dismiss" class="button">Descartar</a>',
                reverse('admin:accounts_report_changelist'),
                obj.id,
                reverse('admin:accounts_report_changelist'),
                obj.id,
            )
        return '-'
    action_buttons.short_description = 'Ações'
    
    def mark_resolved(self, request, queryset):
        updated = queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{updated} denúncias marcadas como resolvidas.')
    mark_resolved.short_description = 'Marcar como resolvidas'
    
    def mark_dismissed(self, request, queryset):
        updated = queryset.update(status='dismissed', resolved_at=timezone.now())
        self.message_user(request, f'{updated} denúncias descartadas.')
    mark_dismissed.short_description = 'Descartar denúncias'
    
    def block_reported_user(self, request, queryset):
        blocked_count = 0
        for report in queryset:
            if report.reported_professional and not report.reported_professional.is_blocked:
                report.reported_professional.is_blocked = True
                report.reported_professional.save()
                blocked_count += 1
            elif report.reported_client and not report.reported_client.is_blocked:
                report.reported_client.is_blocked = True
                report.reported_client.save()
                blocked_count += 1
        self.message_user(request, f'{blocked_count} usuários bloqueados.')
    block_reported_user.short_description = 'Bloquear usuários denunciados'
