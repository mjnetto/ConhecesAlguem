from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Review


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
