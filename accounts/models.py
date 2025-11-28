from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from locations.models import Province, City, Neighborhood


class Client(models.Model):
    """Client/User model - Phone-based authentication only"""
    phone_number = PhoneNumberField(unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_expires_at = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Reporting system
    is_blocked = models.BooleanField(default=False, verbose_name="Conta Bloqueada")
    report_count = models.IntegerField(default=0, verbose_name="Número de Denúncias")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
    
    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class Professional(models.Model):
    """Professional/Service Provider model"""
    phone_number = PhoneNumberField(unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    
    # Required for activation
    nif = models.CharField(max_length=20, verbose_name="NIF")
    iban = models.CharField(max_length=34, verbose_name="IBAN")
    
    # Profile
    profile_picture = models.ImageField(upload_to='professionals/profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Activation
    is_activated = models.BooleanField(default=False, verbose_name="Conta Ativada")
    activated_at = models.DateTimeField(blank=True, null=True)
    activation_notes = models.TextField(blank=True, null=True, help_text="Notas do administrador")
    
    # Contact mode
    CONTACT_MODE_CHOICES = [
        ('booking', 'Apenas por Agendamento (via sistema)'),
        ('direct', 'Contato Direto (mostrar telefone/WhatsApp)'),
    ]
    contact_mode = models.CharField(
        max_length=20,
        choices=CONTACT_MODE_CHOICES,
        default='booking',
        verbose_name="Modo de Contato",
        help_text="Como os clientes podem entrar em contato com você"
    )
    
    # Service areas
    service_provinces = models.ManyToManyField(Province, related_name='professionals')
    service_cities = models.ManyToManyField(City, related_name='professionals', blank=True)
    service_neighborhoods = models.ManyToManyField(Neighborhood, related_name='professionals', blank=True)
    
    # Stats
    total_bookings = models.IntegerField(default=0)
    completed_bookings = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
    # Online status
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name="Última vez online")
    
    # Reporting system
    is_blocked = models.BooleanField(default=False, verbose_name="Conta Bloqueada")
    report_count = models.IntegerField(default=0, verbose_name="Número de Denúncias")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"
    
    def __str__(self):
        status = "Ativado" if self.is_activated else "Pendente"
        return f"{self.name} ({self.phone_number}) - {status}"
    
    def update_rating(self):
        """Recalculate average rating from reviews"""
        from reviews.models import Review
        reviews = Review.objects.filter(booking__professional=self, booking__status='completed')
        if reviews.exists():
            self.average_rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0.00
            self.save(update_fields=['average_rating'])
    
    def get_whatsapp_number(self):
        """Returns phone number formatted for WhatsApp URL (without + and spaces)"""
        phone_str = str(self.phone_number)
        # Remove +, spaces, dashes, parentheses
        return phone_str.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    def get_profile_views_count(self, period='all'):
        """Get profile views count for a specific period"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == 'year':
            start_date = now - timedelta(days=365)
        else:  # 'all'
            return self.profile_views.count()
        
        return self.profile_views.filter(created_at__gte=start_date).count()
    
    def is_online(self):
        """Check if professional is currently online (active in last 10 minutes)"""
        if not self.last_seen:
            return False
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        ten_minutes_ago = now - timedelta(minutes=10)
        return self.last_seen >= ten_minutes_ago
    
    def get_last_seen_display(self):
        """Get human-readable last seen display"""
        if not self.last_seen:
            return "Nunca esteve online"
        
        from django.utils import timezone
        from django.utils.timesince import timesince
        
        now = timezone.now()
        time_diff = now - self.last_seen
        
        # If online (within last 10 minutes)
        if self.is_online():
            return "Online agora"
        
        # Less than 1 hour ago
        if time_diff.total_seconds() < 3600:
            minutes = int(time_diff.total_seconds() / 60)
            if minutes == 0:
                return "Online agora"
            return f"Online há {minutes} min"
        
        # Less than 24 hours ago
        if time_diff.days == 0:
            hours = int(time_diff.total_seconds() / 3600)
            return f"Online há {hours} hora{'s' if hours > 1 else ''}"
        
        # Less than 7 days ago
        if time_diff.days < 7:
            return f"Online há {time_diff.days} dia{'s' if time_diff.days > 1 else ''}"
        
        # More than 7 days - show date
        from django.utils import dateformat
        return f"Online em {dateformat.format(self.last_seen, 'd/m/Y')}"


class PortfolioItem(models.Model):
    """Professional portfolio images"""
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='portfolio_items')
    image = models.ImageField(upload_to='professionals/portfolio/')
    description = models.TextField(blank=True, null=True)
    service_category = models.ForeignKey('services.ServiceCategory', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Item do Portfólio"
        verbose_name_plural = "Itens do Portfólio"
    
    def __str__(self):
        return f"Portfólio de {self.professional.name}"


class ProfileView(models.Model):
    """Track profile views for professionals"""
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='profile_views')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Visualização de Perfil"
        verbose_name_plural = "Visualizações de Perfil"
        indexes = [
            models.Index(fields=['professional', '-created_at']),
        ]
    
    def __str__(self):
        return f"Visualização de {self.professional.name} em {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class Report(models.Model):
    """Report/Complaint model for reporting professionals or clients"""
    REASON_CHOICES = [
        ('fake_profile', 'Perfil Falso ou Suspeito'),
        ('inappropriate_content', 'Conteúdo Inadequado'),
        ('spam', 'Spam ou Comportamento Abusivo'),
        ('scam', 'Golpe ou Fraude'),
        ('harassment', 'Assédio ou Bullying'),
        ('poor_service', 'Serviço de Baixa Qualidade'),
        ('no_show', 'Não Compareceu ao Serviço'),
        ('other', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('reviewing', 'Em Análise'),
        ('resolved', 'Resolvido'),
        ('dismissed', 'Descartado'),
    ]
    
    # Who reported (can be Client or Professional)
    reporter_client = models.ForeignKey(
        'Client', 
        on_delete=models.CASCADE, 
        related_name='reports_made', 
        null=True, 
        blank=True
    )
    reporter_professional = models.ForeignKey(
        'Professional', 
        on_delete=models.CASCADE, 
        related_name='reports_made', 
        null=True, 
        blank=True
    )
    
    # Who is being reported
    reported_professional = models.ForeignKey(
        'Professional', 
        on_delete=models.CASCADE, 
        related_name='reports_received', 
        null=True, 
        blank=True
    )
    reported_client = models.ForeignKey(
        'Client', 
        on_delete=models.CASCADE, 
        related_name='reports_received', 
        null=True, 
        blank=True
    )
    
    # Report details
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, verbose_name="Motivo")
    description = models.TextField(verbose_name="Descrição", help_text="Descreva o problema em detalhes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    
    # Admin notes
    admin_notes = models.TextField(blank=True, null=True, verbose_name="Notas do Administrador")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Resolvido em")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Denúncia"
        verbose_name_plural = "Denúncias"
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['reported_professional', '-created_at']),
            models.Index(fields=['reported_client', '-created_at']),
        ]
    
    def __str__(self):
        reported = self.reported_professional or self.reported_client
        reporter = self.reporter_client or self.reporter_professional
        return f"Denúncia: {reported} por {reporter} - {self.get_reason_display()}"
    
    def clean(self):
        """Ensure either reported_professional or reported_client is set, but not both"""
        from django.core.exceptions import ValidationError
        if not self.reported_professional and not self.reported_client:
            raise ValidationError('Deve ser denunciado um profissional ou cliente.')
        if self.reported_professional and self.reported_client:
            raise ValidationError('Só pode denunciar um profissional ou cliente por vez.')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
