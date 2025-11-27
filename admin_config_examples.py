"""
Django Admin Configuration Examples

Copy these configurations to your respective admin.py files to get a professional admin interface.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe


# ============================================================================
# LOCATIONS APP - admin.py
# ============================================================================

from locations.models import Province, City, Neighborhood


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'city_count', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at']
    
    def city_count(self, obj):
        return obj.cities.count()
    city_count.short_description = 'Número de Cidades'


class NeighborhoodInline(admin.TabularInline):
    model = Neighborhood
    extra = 1
    fields = ['name']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'province', 'neighborhood_count']
    list_filter = ['province']
    search_fields = ['name', 'province__name']
    inlines = [NeighborhoodInline]
    
    def neighborhood_count(self, obj):
        return obj.neighborhoods.count()
    neighborhood_count.short_description = 'Número de Bairros'


@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'province']
    list_filter = ['city__province', 'city']
    search_fields = ['name', 'city__name']
    
    def province(self, obj):
        return obj.city.province.name
    province.short_description = 'Província'


# ============================================================================
# ACCOUNTS APP - admin.py
# ============================================================================

from accounts.models import Client, Professional, PortfolioItem


class PortfolioItemInline(admin.TabularInline):
    model = PortfolioItem
    extra = 1
    fields = ['image', 'description', 'service_category']
    readonly_fields = ['created_at']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'email', 'is_verified', 'booking_count', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['name', 'phone_number', 'email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('name', 'phone_number', 'email')
        }),
        ('Verificação', {
            'fields': ('is_verified', 'verification_code', 'code_expires_at')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
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
    list_filter = ['is_activated', 'created_provinces', 'created_at']
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
        updated = queryset.update(
            is_activated=True, 
            activated_at=timezone.now()
        )
        self.message_user(request, f'{updated} profissionais ativados com sucesso.')
    activate_professionals.short_description = 'Ativar profissionais selecionados'
    
    def deactivate_professionals(self, request, queryset):
        updated = queryset.update(is_activated=False)
        self.message_user(request, f'{updated} profissionais desativados.')
    deactivate_professionals.short_description = 'Desativar profissionais selecionados'


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ['professional', 'service_category', 'image_preview', 'created_at']
    list_filter = ['service_category', 'created_at']
    search_fields = ['professional__name', 'description']
    readonly_fields = ['image_preview', 'created_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.image.url
            )
        return 'Sem imagem'
    image_preview.short_description = 'Preview'


# ============================================================================
# SERVICES APP - admin.py
# ============================================================================

from services.models import ServiceCategory, ServiceSubcategory, ProfessionalService


class ServiceSubcategoryInline(admin.TabularInline):
    model = ServiceSubcategory
    extra = 1
    fields = ['name', 'description', 'is_active', 'sort_order']


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_preview', 'subcategory_count', 'is_active', 'sort_order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'name_en', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ServiceSubcategoryInline]
    
    def icon_preview(self, obj):
        if obj.icon_url:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;" />',
                obj.icon_url
            )
        return 'Sem ícone'
    icon_preview.short_description = 'Ícone'
    
    def subcategory_count(self, obj):
        return obj.subcategories.count()
    subcategory_count.short_description = 'Subcategorias'


@admin.register(ServiceSubcategory)
class ServiceSubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'sort_order']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'category__name', 'description']


@admin.register(ProfessionalService)
class ProfessionalServiceAdmin(admin.ModelAdmin):
    list_display = ['professional', 'category', 'subcategory', 'base_price', 'is_active']
    list_filter = ['category', 'subcategory', 'is_active', 'created_at']
    search_fields = ['professional__name', 'category__name', 'description']
    readonly_fields = ['created_at', 'updated_at']


# ============================================================================
# BOOKINGS APP - admin.py
# ============================================================================

from bookings.models import Booking


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


# ============================================================================
# REVIEWS APP - admin.py
# ============================================================================

from reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'booking_link',
        'professional',
        'rating_stars',
        'comment_preview',
        'is_approved',
        'created_at'
    ]
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = [
        'booking__client__name',
        'booking__professional__name',
        'comment'
    ]
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_reviews', 'disapprove_reviews']
    
    fieldsets = (
        ('Reserva', {
            'fields': ('booking',)
        }),
        ('Avaliação', {
            'fields': ('rating', 'comment')
        }),
        ('Moderação', {
            'fields': ('is_approved',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def booking_link(self, obj):
        url = reverse('admin:bookings_booking_change', args=[obj.booking.id])
        return format_html('<a href="{}">Reserva #{}</a>', url, obj.booking.id)
    booking_link.short_description = 'Reserva'
    
    def professional(self, obj):
        return obj.booking.professional.name
    professional.short_description = 'Profissional'
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: gold; font-size: 16px;">{}</span>', stars)
    rating_stars.short_description = 'Avaliação'
    
    def comment_preview(self, obj):
        if obj.comment:
            preview = obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
            return preview
        return '-'
    comment_preview.short_description = 'Comentário'
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} avaliações aprovadas.')
    approve_reviews.short_description = 'Aprovar avaliações selecionadas'
    
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} avaliações desaprovadas.')
    disapprove_reviews.short_description = 'Desaprovar avaliações selecionadas'


# ============================================================================
# CUSTOM ADMIN SITE CONFIGURATION (Optional)
# ============================================================================

# In core/admin.py or create a custom admin.py in the root:

from django.contrib.admin import AdminSite

class ConhecesAlguemAdminSite(AdminSite):
    site_header = 'Conheces Alguém? - Administração'
    site_title = 'Conheces Alguém? Admin'
    index_title = 'Painel de Administração'

# Uncomment to use custom admin site:
# admin_site = ConhecesAlguemAdminSite(name='conheces_alguem_admin')

