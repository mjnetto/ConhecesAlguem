from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Booking
from services.models import ServiceCategory
from accounts.models import Professional, Client
from locations.models import Province, City, Neighborhood


def booking_step1_service(request, category_id):
    """Step 1: Service selection and task description"""
    category = get_object_or_404(ServiceCategory, id=category_id, is_active=True)
    
    if request.method == 'POST':
        service_description = request.POST.get('service_description', '').strip()
        
        if not service_description:
            messages.error(request, 'Por favor, descreva a tarefa que precisa.')
            return render(request, 'bookings/step1_service.html', {'category': category})
        
        # Store in session
        request.session['booking_category_id'] = category_id
        request.session['booking_service_description'] = service_description
        
        return redirect('bookings:step2_location')
    
    return render(request, 'bookings/step1_service.html', {
        'category': category
    })


def booking_step2_location(request):
    """Step 2: Location selection"""
    # Check if step 1 was completed
    if 'booking_category_id' not in request.session:
        messages.warning(request, 'Por favor, selecione um serviço primeiro.')
        return redirect('home')
    
    provinces = Province.objects.all().order_by('name')
    cities = City.objects.none()
    neighborhoods = Neighborhood.objects.none()
    
    selected_province_id = None
    selected_city_id = None
    
    if request.method == 'POST':
        province_id = request.POST.get('province')
        city_id = request.POST.get('city')
        neighborhood_id = request.POST.get('neighborhood')
        address_line = request.POST.get('address_line', '').strip()
        
        if not province_id:
            messages.error(request, 'Por favor, selecione uma província.')
            return render(request, 'bookings/step2_location.html', {
                'provinces': provinces,
                'cities': cities,
                'neighborhoods': neighborhoods,
            })
        
        # Store in session
        request.session['booking_province_id'] = province_id
        if city_id:
            request.session['booking_city_id'] = city_id
        if neighborhood_id:
            request.session['booking_neighborhood_id'] = neighborhood_id
        request.session['booking_address_line'] = address_line
        
        return redirect('bookings:step3_professional')
    
    return render(request, 'bookings/step2_location.html', {
        'provinces': provinces,
    })


def booking_step3_professional(request):
    """Step 3: Professional selection"""
    # Check if previous steps were completed
    if 'booking_category_id' not in request.session or 'booking_province_id' not in request.session:
        messages.warning(request, 'Por favor, complete os passos anteriores.')
        return redirect('home')
    
    category_id = request.session.get('booking_category_id')
    province_id = request.session.get('booking_province_id')
    city_id = request.session.get('booking_city_id')
    neighborhood_id = request.session.get('booking_neighborhood_id')
    
    category = get_object_or_404(ServiceCategory, id=category_id)
    province = get_object_or_404(Province, id=province_id)
    
    # Get available professionals
    professionals = Professional.objects.filter(
        is_activated=True,
        service_provinces=province,
        professional_services__category=category,
        professional_services__is_active=True
    ).distinct()
    
    # Additional filters
    if city_id:
        professionals = professionals.filter(service_cities__id=city_id)
    
    # Order by rating (best first)
    professionals = professionals.order_by('-average_rating', '-completed_bookings')
    
    return render(request, 'bookings/step3_professional.html', {
        'category': category,
        'province': province,
        'professionals': professionals,
    })


def booking_confirm(request, professional_id):
    """Confirm booking with professional"""
    # Check if previous steps were completed
    if 'booking_category_id' not in request.session:
        messages.warning(request, 'Por favor, complete os passos anteriores.')
        return redirect('home')
    
    professional = get_object_or_404(Professional, id=professional_id, is_activated=True)
    
    if request.method == 'POST':
        # Get or create client
        phone_number = request.POST.get('phone_number', '').strip()
        client_name = request.POST.get('client_name', '').strip()
        
        if not phone_number or not client_name:
            messages.error(request, 'Por favor, preencha seu nome e telefone.')
            return render(request, 'bookings/confirm.html', {
                'professional': professional
            })
        
        # Get or create client
        client, created = Client.objects.get_or_create(
            phone_number=phone_number,
            defaults={'name': client_name, 'is_verified': True}
        )
        if not created:
            client.name = client_name
            client.save()
        
        # Get booking data from session
        category_id = request.session.get('booking_category_id')
        service_description = request.session.get('booking_service_description')
        province_id = request.session.get('booking_province_id')
        city_id = request.session.get('booking_city_id')
        neighborhood_id = request.session.get('booking_neighborhood_id')
        address_line = request.session.get('booking_address_line', '')
        
        # Get professional service
        from services.models import ProfessionalService
        try:
            professional_service = ProfessionalService.objects.filter(
                professional=professional,
                category_id=category_id,
                is_active=True
            ).first()
            
            if not professional_service:
                messages.error(request, 'Este profissional não oferece este serviço.')
                return redirect('bookings:step3_professional')
        except ProfessionalService.DoesNotExist:
            messages.error(request, 'Serviço não encontrado.')
            return redirect('home')
        
        # Create booking
        booking = Booking.objects.create(
            client=client,
            professional=professional,
            service=professional_service,
            province_id=province_id,
            city_id=city_id if city_id else None,
            neighborhood_id=neighborhood_id if neighborhood_id else None,
            address_line=address_line,
            service_description=service_description,
            scheduled_date=request.POST.get('scheduled_date'),
            scheduled_time=request.POST.get('scheduled_time'),
            special_instructions=request.POST.get('special_instructions', ''),
        )
        
        # Clear session
        for key in list(request.session.keys()):
            if key.startswith('booking_'):
                del request.session[key]
        
        # Update professional stats
        professional.total_bookings += 1
        professional.save(update_fields=['total_bookings'])
        
        return redirect('bookings:success', booking_id=booking.id)
    
    return render(request, 'bookings/confirm.html', {
        'professional': professional
    })


def booking_success(request, booking_id):
    """Show booking success page"""
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'bookings/success.html', {
        'booking': booking
    })
