"""
URL configuration for Conheces Alguém? project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

# Customize admin site
admin.site.site_header = "Conheces Alguém? - Administração"
admin.site.site_title = "Conheces Alguém? Admin"
admin.site.index_title = "Painel de Administração"


def home(request):
    """Homepage with service categories"""
    from services.models import ServiceCategory
    categories = ServiceCategory.objects.filter(is_active=True).order_by('sort_order', 'name')
    context = {
        'service_categories': categories,
    }
    return render(request, 'home.html', context)




def service_category(request, slug):
    """Temporary view for service category"""
    from services.models import ServiceCategory
    try:
        category = ServiceCategory.objects.get(slug=slug)
        return render(request, 'coming_soon.html', {'page': f'Categoria: {category.name}'})
    except ServiceCategory.DoesNotExist:
        from django.http import Http404
        raise Http404


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    # App URLs
    path('services/', include('services.urls')),
    path('bookings/', include('bookings.urls')),
    path('locations/', include('locations.urls')),
    path('accounts/', include('accounts.urls')),
    path('reviews/', include('reviews.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

