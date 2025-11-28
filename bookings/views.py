from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Booking
from .forms import BookingConfirmForm
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
        
        # Store in session (ensure category_id is int)
        request.session['booking_category_id'] = int(category_id)
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
        
        # Store in session (ensure IDs are ints)
        request.session['booking_province_id'] = int(province_id)
        if city_id:
            request.session['booking_city_id'] = int(city_id)
        if neighborhood_id:
            request.session['booking_neighborhood_id'] = int(neighborhood_id)
        request.session['booking_address_line'] = address_line
        
        return redirect('bookings:step3_professional')
    
    return render(request, 'bookings/step2_location.html', {
        'provinces': provinces,
    })


def booking_step3_professional(request):
    """Step 3: Professional selection"""
    # Check if previous steps were completed
    if 'booking_category_id' not in request.session or 'booking_province_id' not in request.session:
        messages.warning(request, 'Por favor, complete os passos anteriores (escolha um serviço e localização).')
        return redirect('home')
    
    # Get IDs from session (they should already be ints, but ensure they are)
    try:
        category_id = int(request.session.get('booking_category_id'))
        province_id = int(request.session.get('booking_province_id'))
        city_id = int(request.session.get('booking_city_id')) if request.session.get('booking_city_id') else None
        neighborhood_id = int(request.session.get('booking_neighborhood_id')) if request.session.get('booking_neighborhood_id') else None
    except (ValueError, TypeError):
        messages.error(request, 'Erro ao processar dados da sessão. Por favor, tente novamente.')
        return redirect('home')
    
    category = get_object_or_404(ServiceCategory, id=category_id)
    province = get_object_or_404(Province, id=province_id)
    
    # Debug info (can be removed in production)
    total_professionals = Professional.objects.filter(is_activated=True, is_blocked=False).count()
    professionals_in_province = Professional.objects.filter(
        is_activated=True,
        is_blocked=False,
        service_provinces=province
    ).count()
    professionals_with_category = Professional.objects.filter(
        is_activated=True,
        is_blocked=False,
        professional_services__category=category,
        professional_services__is_active=True
    ).distinct().count()
    
    # Get available professionals
    professionals = Professional.objects.filter(
        is_activated=True,
        is_blocked=False,
        service_provinces=province,
        professional_services__category=category,
        professional_services__is_active=True
    ).distinct()
    
    # Additional filters
    # Note: If a city is selected, we include professionals who:
    # 1. Work in that specific city, OR
    # 2. Work in the entire province (no specific cities set)
    if city_id:
        from django.db.models import Q
        professionals = professionals.filter(
            Q(service_cities__id=city_id) | Q(service_cities__isnull=True)
        ).distinct()
    
    # Order by rating (best first)
    professionals = professionals.order_by('-average_rating', '-completed_bookings')
    
    # Add helpful message if no professionals found
    if not professionals.exists():
        messages.info(request, 
            f'Nenhum profissional encontrado para "{category.name}" em {province.name}. '
            f'Tente escolher outra categoria ou província, ou volte mais tarde. '
            f'(Há {professionals_in_province} profissionais em {province.name} e {professionals_with_category} oferecem {category.name})'
        )
    
    return render(request, 'bookings/step3_professional.html', {
        'category': category,
        'province': province,
        'professionals': professionals,
        'total_professionals': total_professionals,
        'professionals_in_province': professionals_in_province,
        'professionals_with_category': professionals_with_category,
    })


def booking_confirm(request, professional_id):
    """Confirm booking with professional"""
    # Check if previous steps were completed
    if 'booking_category_id' not in request.session:
        messages.warning(request, 'Por favor, complete os passos anteriores.')
        return redirect('home')
    
    professional = get_object_or_404(Professional, id=professional_id, is_activated=True)
    
    if request.method == 'POST':
        form = BookingConfirmForm(request.POST)
        
        if form.is_valid():
            # Get or create client
            phone_number = form.cleaned_data['phone_number']
            client_name = form.cleaned_data['client_name']
            
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
                scheduled_date=form.cleaned_data['scheduled_date'],
                scheduled_time=form.cleaned_data['scheduled_time'],
                special_instructions=form.cleaned_data.get('special_instructions', ''),
            )
            
            # Clear session
            for key in list(request.session.keys()):
                if key.startswith('booking_'):
                    del request.session[key]
            
            # Update professional stats
            professional.total_bookings += 1
            professional.save(update_fields=['total_bookings'])
            
            # Send email notifications
            from core.emails import send_booking_confirmation_to_client, send_booking_notification_to_professional
            send_booking_confirmation_to_client(booking)
            send_booking_notification_to_professional(booking)
            
            messages.success(request, 'Reserva confirmada com sucesso!')
            return redirect('bookings:success', booking_id=booking.id)
    else:
        form = BookingConfirmForm()
    
    return render(request, 'bookings/confirm.html', {
        'professional': professional,
        'form': form
    })


def booking_success(request, booking_id):
    """Show booking success page"""
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'bookings/success.html', {
        'booking': booking
    })
