from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import Professional, PortfolioItem, Client
from .forms import (
    ProfessionalRegistrationStep1Form,
    ProfessionalRegistrationStep2Form,
    ProfessionalRegistrationStep3Form,
    PortfolioItemForm
)
from services.models import ProfessionalService


def client_login(request):
    """Simple phone-based login for clients"""
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        
        if not phone_number:
            messages.error(request, 'Por favor, informe seu número de telefone.')
            return render(request, 'accounts/client_login.html')
        
        try:
            client = Client.objects.get(phone_number=phone_number)
            # Store client ID in session
            request.session['client_id'] = client.id
            request.session['client_name'] = client.name
            messages.success(request, f'Bem-vindo, {client.name}!')
            
            # Check if there's a pending review after login
            review_booking_id = request.session.get('review_booking_id')
            if review_booking_id:
                request.session.pop('review_booking_id', None)
                return redirect('reviews:create_review', booking_id=review_booking_id)
            
            return redirect('accounts:client_dashboard')
        except Client.DoesNotExist:
            messages.error(request, 'Número de telefone não encontrado. Faça uma reserva primeiro ou verifique o número.')
            return render(request, 'accounts/client_login.html')
    
    return render(request, 'accounts/client_login.html')


def client_dashboard(request):
    """Dashboard for logged-in clients - shows bookings"""
    if 'client_id' not in request.session:
        messages.warning(request, 'Por favor, faça login primeiro.')
        return redirect('accounts:client_login')
    
    client_id = request.session.get('client_id')
    client = get_object_or_404(Client, id=client_id)
    
    # Get bookings
    from bookings.models import Booking
    bookings = Booking.objects.filter(client=client).order_by('-created_at')
    
    # Separate by status
    pending_bookings = bookings.filter(status__in=['pending', 'confirmed', 'in_progress'])
    completed_bookings = bookings.filter(status='completed')
    cancelled_bookings = bookings.filter(status='cancelled')
    
    context = {
        'client': client,
        'pending_bookings': pending_bookings,
        'completed_bookings': completed_bookings,
        'cancelled_bookings': cancelled_bookings,
    }
    
    return render(request, 'accounts/client_dashboard.html', context)


def client_logout(request):
    """Logout client"""
    request.session.pop('client_id', None)
    request.session.pop('client_name', None)
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('home')


def professional_login(request):
    """Simple phone-based login for professionals"""
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        
        if not phone_number:
            messages.error(request, 'Por favor, informe seu número de telefone.')
            return render(request, 'accounts/login.html')
        
        try:
            professional = Professional.objects.get(phone_number=phone_number)
            # Store professional ID in session
            request.session['professional_id'] = professional.id
            request.session['professional_name'] = professional.name
            # Update last seen
            from django.utils import timezone
            professional.last_seen = timezone.now()
            professional.save(update_fields=['last_seen'])
            messages.success(request, f'Bem-vindo, {professional.name}!')
            return redirect('accounts:professional_dashboard')
        except Professional.DoesNotExist:
            messages.error(request, 'Número de telefone não encontrado. Cadastre-se primeiro.')
            return redirect('accounts:register_professional')
    
    return render(request, 'accounts/login.html')


def professional_dashboard(request):
    """Dashboard for logged-in professionals"""
    if 'professional_id' not in request.session:
        messages.warning(request, 'Por favor, faça login primeiro.')
        return redirect('accounts:professional_login')
    
    professional_id = request.session.get('professional_id')
    professional = get_object_or_404(Professional, id=professional_id)
    
    # Update last seen (but only if it's been more than 5 minutes to avoid too many DB writes)
    from django.utils import timezone
    from datetime import timedelta
    if not professional.last_seen or professional.last_seen < timezone.now() - timedelta(minutes=5):
        professional.last_seen = timezone.now()
        professional.save(update_fields=['last_seen'])
    
    # Get bookings
    from bookings.models import Booking
    all_bookings = Booking.objects.filter(professional=professional).order_by('-created_at')
    
    # Separate by status
    pending_bookings = all_bookings.filter(status='pending')
    confirmed_bookings = all_bookings.filter(status='confirmed')
    in_progress_bookings = all_bookings.filter(status='in_progress')
    completed_bookings = all_bookings.filter(status='completed')
    cancelled_bookings = all_bookings.filter(status='cancelled')
    
    # Statistics
    pending_count = pending_bookings.count()
    confirmed_count = confirmed_bookings.count()
    in_progress_count = in_progress_bookings.count()
    completed_count = completed_bookings.count()
    
    context = {
        'professional': professional,
        'pending_bookings': pending_bookings[:10],
        'confirmed_bookings': confirmed_bookings[:10],
        'in_progress_bookings': in_progress_bookings[:10],
        'completed_bookings': completed_bookings[:10],
        'cancelled_bookings': cancelled_bookings[:5],
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
    }
    
    return render(request, 'accounts/professional_dashboard.html', context)


def professional_booking_action(request, booking_id, action):
    """Handle booking actions (accept, reject, start, complete, cancel)"""
    if 'professional_id' not in request.session:
        messages.warning(request, 'Por favor, faça login primeiro.')
        return redirect('accounts:professional_login')
    
    professional_id = request.session.get('professional_id')
    professional = get_object_or_404(Professional, id=professional_id)
    
    from bookings.models import Booking
    from django.utils import timezone
    from core.emails import send_booking_status_update_to_client
    
    booking = get_object_or_404(Booking, id=booking_id, professional=professional)
    old_status = booking.status
    
    if action == 'accept':
        if booking.status == 'pending':
            booking.status = 'confirmed'
            booking.save(update_fields=['status'])
            # Send email notification
            send_booking_status_update_to_client(booking, old_status)
            messages.success(request, f'Reserva #{booking.id} confirmada com sucesso!')
        else:
            messages.error(request, 'Esta reserva não pode ser confirmada no estado atual.')
    
    elif action == 'reject':
        if booking.status in ['pending', 'confirmed']:
            booking.status = 'cancelled'
            booking.save(update_fields=['status'])
            # Send email notification
            send_booking_status_update_to_client(booking, old_status)
            messages.success(request, f'Reserva #{booking.id} cancelada.')
        else:
            messages.error(request, 'Esta reserva não pode ser cancelada no estado atual.')
    
    elif action == 'start':
        if booking.status == 'confirmed':
            booking.status = 'in_progress'
            booking.save(update_fields=['status'])
            # Send email notification
            send_booking_status_update_to_client(booking, old_status)
            messages.success(request, f'Iniciou o trabalho na reserva #{booking.id}!')
        else:
            messages.error(request, 'Esta reserva não pode ser iniciada no estado atual.')
    
    elif action == 'complete':
        if booking.status == 'in_progress':
            booking.status = 'completed'
            booking.completed_at = timezone.now()
            booking.save(update_fields=['status', 'completed_at'])
            
            # Update professional stats
            professional.completed_bookings += 1
            professional.save(update_fields=['completed_bookings'])
            
            # Send email notification
            send_booking_status_update_to_client(booking, old_status)
            messages.success(request, f'Reserva #{booking.id} marcada como concluída!')
        else:
            messages.error(request, 'Esta reserva não pode ser concluída no estado atual.')
    
    else:
        messages.error(request, 'Ação inválida.')
    
    return redirect('accounts:professional_dashboard')


def professional_logout(request):
    """Logout professional"""
    request.session.pop('professional_id', None)
    request.session.pop('professional_name', None)
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('home')


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
            
            # Send notification to admin
            from core.emails import send_professional_registration_notification
            send_professional_registration_notification(professional)
            
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


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def professional_profile(request, pk):
    """Public profile page for a professional"""
    professional = get_object_or_404(Professional, pk=pk, is_activated=True)
    
    # Track profile view (only if not viewing own profile)
    if request.session.get('professional_id') != professional.id:
        from .models import ProfileView
        ProfileView.objects.create(
            professional=professional,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]  # Limit length
        )
    
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
