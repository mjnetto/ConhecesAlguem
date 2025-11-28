from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import ServiceCategory, ProfessionalService
from accounts.models import Professional


def category_list(request):
    """List all service categories"""
    categories = ServiceCategory.objects.filter(is_active=True).order_by('sort_order', 'name')
    
    # Process search_keywords for each category to create a list of tasks
    for category in categories:
        if category.search_keywords:
            # Split by comma and clean up
            category.tasks = [task.strip() for task in category.search_keywords.split(',') if task.strip()][:8]
        else:
            category.tasks = []
    
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
    """List professionals by category with filters"""
    from locations.models import Province, City
    from django.db.models import Q
    
    category = get_object_or_404(ServiceCategory, slug=slug, is_active=True)
    
    # Get filter parameters
    province_id = request.GET.get('province')
    city_id = request.GET.get('city')
    min_rating = request.GET.get('min_rating')
    sort_by = request.GET.get('sort', 'rating')  # rating, bookings, name
    
    # Base queryset
    professionals = Professional.objects.filter(
        is_activated=True,
        professional_services__category=category,
        professional_services__is_active=True
    ).distinct()
    
    # Apply location filters
    if province_id:
        professionals = professionals.filter(service_provinces__id=province_id)
        
        # If city is selected, show professionals in that city OR professionals without city restriction
        if city_id:
            professionals = professionals.filter(
                Q(service_cities__id=city_id) | Q(service_cities__isnull=True)
            ).distinct()
    
    # Apply rating filter
    if min_rating:
        try:
            min_rating_float = float(min_rating)
            professionals = professionals.filter(average_rating__gte=min_rating_float)
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'rating':
        professionals = professionals.order_by('-average_rating', '-completed_bookings', 'name')
    elif sort_by == 'bookings':
        professionals = professionals.order_by('-completed_bookings', '-average_rating', 'name')
    elif sort_by == 'name':
        professionals = professionals.order_by('name')
    else:
        professionals = professionals.order_by('-average_rating', '-completed_bookings', 'name')
    
    # Get provinces for filter dropdown
    provinces = Province.objects.all().order_by('name')
    cities = City.objects.none()
    if province_id:
        cities = City.objects.filter(province_id=province_id).order_by('name')
    
    return render(request, 'services/professionals_list.html', {
        'category': category,
        'professionals': professionals,
        'provinces': provinces,
        'cities': cities,
        'province_id': int(province_id) if province_id else None,
        'city_id': int(city_id) if city_id else None,
        'min_rating': min_rating,
        'sort_by': sort_by,
    })
