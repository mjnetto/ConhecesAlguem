from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count
from .models import Professional, PortfolioItem
from .forms import (
    ProfessionalRegistrationStep1Form,
    ProfessionalRegistrationStep2Form,
    ProfessionalRegistrationStep3Form,
    PortfolioItemForm
)
from services.models import ProfessionalService


@require_http_methods(["GET", "POST"])
def register_professional(request):
    """Step 1: Basic information"""
    if request.method == 'POST':
        form = ProfessionalRegistrationStep1Form(request.POST)
        if form.is_valid():
            # Check if professional already exists
            phone_number = form.cleaned_data['phone_number']
            if Professional.objects.filter(phone_number=phone_number).exists():
                messages.error(request, 'Este número de telefone já está cadastrado.')
                return render(request, 'accounts/register_professional_step1.html', {'form': form})
            
            # Store in session
            request.session['professional_data'] = {
                'name': form.cleaned_data['name'],
                'phone_number': str(phone_number),
                'email': form.cleaned_data.get('email', ''),
            }
            return redirect('accounts:register_professional_step2')
    else:
        form = ProfessionalRegistrationStep1Form()
    
    return render(request, 'accounts/register_professional_step1.html', {
        'form': form,
        'step': 1,
        'total_steps': 4
    })


@require_http_methods(["GET", "POST"])
def register_professional_step2(request):
    """Step 2: Documents and profile"""
    if 'professional_data' not in request.session:
        messages.warning(request, 'Por favor, complete a etapa anterior.')
        return redirect('accounts:register_professional')
    
    if request.method == 'POST':
        form = ProfessionalRegistrationStep2Form(request.POST, request.FILES)
        if form.is_valid():
            # Update session
            request.session['professional_data'].update({
                'nif': form.cleaned_data['nif'],
                'iban': form.cleaned_data['iban'],
                'bio': form.cleaned_data.get('bio', ''),
            })
            
            # Note: Profile picture upload skipped for MVP to avoid session issues
            # Professionals can add profile picture later via admin
            
            return redirect('accounts:register_professional_step3')
    else:
        form = ProfessionalRegistrationStep2Form()
    
    return render(request, 'accounts/register_professional_step2.html', {
        'form': form,
        'step': 2,
        'total_steps': 4
    })


@require_http_methods(["GET", "POST"])
def register_professional_step3(request):
    """Step 3: Service categories and areas"""
    if 'professional_data' not in request.session:
        messages.warning(request, 'Por favor, complete as etapas anteriores.')
        return redirect('accounts:register_professional')
    
    if request.method == 'POST':
        form = ProfessionalRegistrationStep3Form(request.POST)
        if form.is_valid():
            # Update session
            request.session['professional_data'].update({
                'service_categories': [str(cat.id) for cat in form.cleaned_data['service_categories']],
                'service_provinces': [str(prov.id) for prov in form.cleaned_data['service_provinces']],
                'service_cities': [str(city.id) for city in form.cleaned_data.get('service_cities', [])],
            })
            
            # Create professional
            from phonenumber_field.phonenumber import PhoneNumber
            from locations.models import Province, City
            from services.models import ServiceCategory
            
            data = request.session['professional_data']
            phone_number = PhoneNumber.from_string(data['phone_number'], region='AO')
            
            # Create professional
            professional = Professional.objects.create(
                name=data['name'],
                phone_number=phone_number,
                email=data.get('email') or None,
                nif=data['nif'],
                iban=data['iban'],
                bio=data.get('bio', ''),
                is_activated=False,  # Needs admin approval
            )
            
            # Profile picture: Skip for MVP - can be added later via admin
            # This avoids session storage issues with large files
            
            # Add service areas
            provinces = Province.objects.filter(id__in=data['service_provinces'])
            professional.service_provinces.set(provinces)
            
            cities = City.objects.filter(id__in=data.get('service_cities', []))
            professional.service_cities.set(cities)
            
            # Create professional services
            categories = ServiceCategory.objects.filter(id__in=data['service_categories'])
            for category in categories:
                ProfessionalService.objects.create(
                    professional=professional,
                    category=category,
                    description=f'Serviço de {category.name}',
                    is_active=True
                )
            
            # Store professional ID in session for portfolio step
            request.session['professional_id'] = professional.id
            
            return redirect('accounts:register_professional_portfolio')
    else:
        form = ProfessionalRegistrationStep3Form()
    
    return render(request, 'accounts/register_professional_step3.html', {
        'form': form,
        'step': 3,
        'total_steps': 4
    })


@require_http_methods(["GET", "POST"])
def register_professional_portfolio(request):
    """Step 4: Portfolio (optional)"""
    if 'professional_id' not in request.session:
        messages.warning(request, 'Por favor, complete as etapas anteriores.')
        return redirect('accounts:register_professional')
    
    professional_id = request.session.get('professional_id')
    professional = Professional.objects.get(id=professional_id)
    
    if request.method == 'POST':
        # Check if user wants to skip or add more
        if 'skip' in request.POST:
            # Clear session and redirect to success
            request.session.pop('professional_data', None)
            request.session.pop('professional_id', None)
            return redirect('accounts:register_professional_success', professional_id=professional.id)
        
        # Handle portfolio items
        if 'portfolio_images' in request.FILES:
            files = request.FILES.getlist('portfolio_images')
            descriptions = request.POST.getlist('portfolio_descriptions')
            
            for i, file in enumerate(files):
                description = descriptions[i] if i < len(descriptions) else ''
                PortfolioItem.objects.create(
                    professional=professional,
                    image=file,
                    description=description
                )
        
        # Clear session and redirect to success
        request.session.pop('professional_data', None)
        request.session.pop('professional_id', None)
        return redirect('accounts:register_professional_success', professional_id=professional.id)
    
    return render(request, 'accounts/register_professional_portfolio.html', {
        'professional': professional,
        'step': 4,
        'total_steps': 4
    })


def register_professional_success(request, professional_id):
    """Success page"""
    professional = Professional.objects.get(id=professional_id)
    
    return render(request, 'accounts/register_professional_success.html', {
        'professional': professional
    })


def professional_profile(request, pk):
    """Public profile page for a professional"""
    professional = get_object_or_404(Professional, pk=pk, is_activated=True)
    
    # Get portfolio items
    portfolio_items = professional.portfolio_items.all()[:12]
    
    # Get reviews (approved only)
    from reviews.models import Review
    reviews = Review.objects.filter(
        booking__professional=professional,
        is_approved=True
    ).select_related('booking__client').order_by('-created_at')[:10]
    
    # Get services offered
    services = professional.professional_services.filter(is_active=True).select_related('category', 'subcategory')
    
    # Get service areas
    provinces = professional.service_provinces.all()
    cities = professional.service_cities.all()
    neighborhoods = professional.service_neighborhoods.all()
    
    # Statistics
    total_reviews = Review.objects.filter(booking__professional=professional, is_approved=True).count()
    completed_bookings = professional.completed_bookings
    
    context = {
        'professional': professional,
        'portfolio_items': portfolio_items,
        'reviews': reviews,
        'services': services,
        'provinces': provinces,
        'cities': cities,
        'neighborhoods': neighborhoods,
        'total_reviews': total_reviews,
        'completed_bookings': completed_bookings,
    }
    
    return render(request, 'accounts/professional_profile.html', context)

