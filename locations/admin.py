from django.contrib import admin
from .models import Province, City, Neighborhood


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
