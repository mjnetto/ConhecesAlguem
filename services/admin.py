from django.contrib import admin
from django.utils.html import format_html
from .models import ServiceCategory, ServiceSubcategory, ProfessionalService


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
