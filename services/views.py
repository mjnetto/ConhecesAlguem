from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import ServiceCategory, ProfessionalService
from accounts.models import Professional


def category_list(request):
    """List all service categories"""
    categories = ServiceCategory.objects.filter(is_active=True).order_by('sort_order', 'name')
    return render(request, 'services/category_list.html', {
        'categories': categories
    })


def category_detail(request, slug):
    """Show category details and start booking"""
    category = get_object_or_404(ServiceCategory, slug=slug, is_active=True)
    
    # Get professionals offering this service
    professionals = Professional.objects.filter(
        is_activated=True,
        professional_services__category=category,
        professional_services__is_active=True
    ).distinct()[:10]  # Limit to 10 for now
    
    return render(request, 'services/category_detail.html', {
        'category': category,
        'professionals': professionals
    })


def professionals_by_category(request, slug):
    """List professionals by category and location"""
    category = get_object_or_404(ServiceCategory, slug=slug, is_active=True)
    
    # Get filter parameters
    province_id = request.GET.get('province')
    city_id = request.GET.get('city')
    
    # Base queryset
    professionals = Professional.objects.filter(
        is_activated=True,
        professional_services__category=category,
        professional_services__is_active=True
    ).distinct()
    
    # Apply location filters
    if province_id:
        professionals = professionals.filter(service_provinces__id=province_id)
    if city_id:
        professionals = professionals.filter(service_cities__id=city_id)
    
    return render(request, 'services/professionals_list.html', {
        'category': category,
        'professionals': professionals,
        'province_id': province_id,
        'city_id': city_id,
    })
