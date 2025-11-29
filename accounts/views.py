from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import Professional, PortfolioItem, Client, Report
from .forms import (
    ProfessionalRegistrationStep1Form,
    ProfessionalRegistrationStep2Form,
    ProfessionalRegistrationStep3Form,
    PortfolioItemForm,
    ReportForm
)
from services.models import ProfessionalService


def google_oauth_callback(request):
    """Handle Google OAuth callback and link to Client or Professional"""
    from allauth.socialaccount.models import SocialAccount
    
    if not request.user.is_authenticated:
        # Redireciona para escolher tipo de usuário
        return redirect('accounts:choose_user_type')
    
    # Busca a conta social do Google
    try:
        social_account = SocialAccount.objects.get(user=request.user, provider='google')
        email = social_account.extra_data.get('email')
        google_id = social_account.uid
        name = social_account.extra_data.get('name', email.split('@')[0])
        
        # Armazena informações na sessão para escolha
        request.session['google_email'] = email
        request.session['google_id'] = google_id
        request.session['google_name'] = name
        
        # Verifica se já existe conta vinculada
        try:
            client = Client.objects.get(google_id=google_id)
            request.session['client_id'] = client.id
            request.session['client_name'] = client.name
            messages.success(request, f'Bem-vindo, {client.name}!')
            return redirect('accounts:client_dashboard')
        except Client.DoesNotExist:
            pass
        
        try:
            professional = Professional.objects.get(google_id=google_id)
            request.session['professional_id'] = professional.id
            request.session['professional_name'] = professional.name
            messages.success(request, f'Bem-vindo, {professional.name}!')
            return redirect('accounts:professional_dashboard')
        except Professional.DoesNotExist:
            pass
        
        # Se não encontrou, redireciona para escolha
        return redirect('accounts:choose_user_type')
        
    except SocialAccount.DoesNotExist:
        messages.error(request, 'Erro ao autenticar com Google.')
        return redirect('accounts:client_login')


def choose_user_type(request):
    """View para escolher se é Client ou Professional após login Google"""
    google_email = request.session.get('google_email')
    google_id = request.session.get('google_id')
    google_name = request.session.get('google_name')
    
    if not google_email:
        messages.warning(request, 'Por favor, faça login com Google primeiro.')
        return redirect('accounts:client_login')
    
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        if user_type == 'client':
            # Criar ou atualizar Client
            client, created = Client.objects.get_or_create(
                email=google_email,
                defaults={
                    'name': google_name,
                    'google_id': google_id,
                    'is_verified': True,
                }
            )
            if not created and not client.google_id:
                client.google_id = google_id
                client.is_verified = True
                client.save()
            
            request.session['client_id'] = client.id
            request.session['client_name'] = client.name
            request.session.pop('google_email', None)
            request.session.pop('google_id', None)
            request.session.pop('google_name', None)
            
            messages.success(request, f'Bem-vindo, {client.name}!')
            return redirect('accounts:client_dashboard')
        
        elif user_type == 'professional':
            # Verifica se já existe profissional com este email
            try:
                professional = Professional.objects.get(email=google_email)
                # Vincula Google ID se ainda não tiver
                if not professional.google_id:
                    professional.google_id = google_id
                    professional.save()
                request.session['professional_id'] = professional.id
                request.session['professional_name'] = professional.name
                request.session.pop('google_email', None)
                request.session.pop('google_id', None)
                request.session.pop('google_name', None)
                messages.success(request, f'Bem-vindo, {professional.name}!')
                return redirect('accounts:professional_dashboard')
            except Professional.DoesNotExist:
                # Redireciona para registro de profissional
                # O email e nome já estarão na sessão
                return redirect('accounts:register_professional')
    
    return render(request, 'accounts/choose_user_type.html', {
        'google_name': google_name,
        'google_email': google_email,
    })


def client_login(request):
    """Login for clients - Phone or Google"""
    # Se já está logado, redireciona
    if 'client_id' in request.session:
        return redirect('accounts:client_dashboard')
    
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
    # Se vier do Google OAuth, pré-preenche dados
    google_email = request.session.get('google_email')
    google_name = request.session.get('google_name')
    google_id = request.session.get('google_id')
    
    # Verifica se usuário está logado como cliente e pode usar os mesmos dados
    existing_client = None
    client_id = request.session.get('client_id')
    if client_id:
        try:
            existing_client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = ProfessionalRegistrationStep1Form(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data.get('email', '')
            
            # Check if professional already exists (mesma tabela)
            if Professional.objects.filter(phone_number=phone_number).exists():
                messages.error(request, 'Já existe um profissional cadastrado com este número de telefone.')
                return render(request, 'accounts/register_professional_step1.html', {
                    'form': form,
                    'step': 1,
                    'total_steps': 4,
                    'existing_client': existing_client,
                })
            
            # Verifica se já existe profissional com este email (mas permite continuar se for o mesmo cliente)
            if email:
                existing_professional = Professional.objects.filter(email=email).first()
                if existing_professional:
                    messages.warning(request, f'Já existe um profissional cadastrado com este email. Por favor, use outro email ou faça login como profissional.')
                    return render(request, 'accounts/register_professional_step1.html', {
                        'form': form,
                        'step': 1,
                        'total_steps': 4,
                        'existing_client': existing_client,
                    })
            
            # Informa se existe cliente com os mesmos dados (mas permite continuar)
            # Não precisa mostrar mensagem duplicada, já aparece no template
            
            # Store in session
            request.session['professional_data'] = {
                'name': form.cleaned_data['name'],
                'phone_number': str(phone_number),
                'email': email,
            }
            return redirect('accounts:register_professional_step2')
    else:
        form = ProfessionalRegistrationStep1Form()
        # Pré-preenche se vier do Google OU se já é cliente
        if existing_client:
            if existing_client.email:
                form.fields['email'].initial = existing_client.email
            if existing_client.name:
                form.fields['name'].initial = existing_client.name
            if existing_client.phone_number:
                form.fields['phone_number'].initial = existing_client.phone_number
        elif google_email:
            form.fields['email'].initial = google_email
        if google_name:
            form.fields['name'].initial = google_name
    
    return render(request, 'accounts/register_professional_step1.html', {
        'form': form,
        'step': 1,
        'total_steps': 4,
        'google_email': google_email,
        'google_name': google_name,
        'existing_client': existing_client,
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
                'nif': form.cleaned_data.get('nif', ''),
                'iban': form.cleaned_data.get('iban', ''),
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
                nif=data.get('nif', ''),
                iban=data.get('iban', '') or '',  # IBAN é opcional
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
    professional = get_object_or_404(
        Professional, 
        pk=pk, 
        is_activated=True,
        is_blocked=False  # Don't show blocked professionals
    )
    
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


@require_http_methods(["GET", "POST"])
def report_professional(request, pk):
    """Report a professional"""
    professional = get_object_or_404(Professional, pk=pk, is_activated=True)
    
    # Can't report yourself
    if request.session.get('professional_id') == professional.id:
        messages.error(request, 'Você não pode denunciar seu próprio perfil.')
        return redirect('accounts:professional_profile', pk=pk)
    
    # Can't report if already blocked
    if professional.is_blocked:
        messages.info(request, 'Este profissional já foi bloqueado.')
        return redirect('accounts:professional_profile', pk=pk)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            # Get reporter (can be client or professional)
            reporter_client = None
            reporter_professional = None
            
            if 'client_id' in request.session:
                try:
                    reporter_client = Client.objects.get(id=request.session['client_id'])
                except Client.DoesNotExist:
                    pass
            elif 'professional_id' in request.session:
                try:
                    reporter_professional = Professional.objects.get(id=request.session['professional_id'])
                except Professional.DoesNotExist:
                    pass
            
            # Check if already reported by this user
            if reporter_client:
                existing = Report.objects.filter(
                    reporter_client=reporter_client,
                    reported_professional=professional,
                    status__in=['pending', 'reviewing']
                ).exists()
            elif reporter_professional:
                existing = Report.objects.filter(
                    reporter_professional=reporter_professional,
                    reported_professional=professional,
                    status__in=['pending', 'reviewing']
                ).exists()
            else:
                existing = False
            
            if existing:
                messages.warning(request, 'Você já denunciou este profissional. Aguarde a análise da nossa equipe.')
                return redirect('accounts:professional_profile', pk=pk)
            
            # Create report
            report = form.save(commit=False)
            report.reporter_client = reporter_client
            report.reporter_professional = reporter_professional
            report.reported_professional = professional
            report.save()
            
            # Update report count
            professional.report_count = Report.objects.filter(
                reported_professional=professional,
                status__in=['pending', 'reviewing']
            ).count()
            professional.save(update_fields=['report_count'])
            
            # Check if should auto-block
            from django.conf import settings
            if professional.report_count >= getattr(settings, 'REPORTS_TO_BLOCK_PROFESSIONAL', 5):
                professional.is_blocked = True
                professional.save(update_fields=['is_blocked'])
                messages.warning(request, 
                    f'Obrigado pela denúncia. Após {settings.REPORTS_TO_BLOCK_PROFESSIONAL} denúncias, '
                    'o perfil foi automaticamente bloqueado para análise.'
                )
            else:
                messages.success(request, 
                    'Denúncia enviada com sucesso. Nossa equipe analisará o caso o mais breve possível.'
                )
            
            return redirect('accounts:professional_profile', pk=pk)
    else:
        form = ReportForm()
    
    from django.conf import settings
    return render(request, 'accounts/report_professional.html', {
        'form': form,
        'professional': professional,
        'reports_to_block': getattr(settings, 'REPORTS_TO_BLOCK_PROFESSIONAL', 5),
    })
