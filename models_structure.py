"""
Django Models Structure for Conheces Alguém?

This file shows the complete model structure. Copy these into your respective app models.py files.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


# ============================================================================
# LOCATIONS APP - models.py
# ============================================================================

class Province(models.Model):
    """Angolan Provinces - 18 provinces"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Província"
        verbose_name_plural = "Províncias"
    
    def __str__(self):
        return self.name


class City(models.Model):
    """Cities within provinces"""
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['province', 'name']
        unique_together = ['name', 'province']
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"
    
    def __str__(self):
        return f"{self.name}, {self.province.name}"


class Neighborhood(models.Model):
    """Neighborhoods (mainly for Luanda)"""
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='neighborhoods')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['city', 'name']
        unique_together = ['name', 'city']
        verbose_name = "Bairro"
        verbose_name_plural = "Bairros"
    
    def __str__(self):
        return f"{self.name}, {self.city.name}"


# ============================================================================
# ACCOUNTS APP - models.py
# ============================================================================

class Client(models.Model):
    """Client/User model - Phone-based authentication only"""
    phone_number = PhoneNumberField(unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_expires_at = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
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
    
    # Service areas
    service_provinces = models.ManyToManyField(Province, related_name='professionals')
    service_cities = models.ManyToManyField(City, related_name='professionals', blank=True)
    service_neighborhoods = models.ManyToManyField(Neighborhood, related_name='professionals', blank=True)
    
    # Stats
    total_bookings = models.IntegerField(default=0)
    completed_bookings = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
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


# ============================================================================
# SERVICES APP - models.py
# ============================================================================

class ServiceCategory(models.Model):
    """Main service categories (e.g., Cleaning, Plumbing)"""
    name = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200, blank=True, null=True)  # English name
    slug = models.SlugField(unique=True)
    icon_url = models.URLField(max_length=500)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Categoria de Serviço"
        verbose_name_plural = "Categorias de Serviço"
    
    def __str__(self):
        return self.name


class ServiceSubcategory(models.Model):
    """Subcategories within a category (e.g., Washing Machines under Appliances)"""
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'sort_order', 'name']
        unique_together = ['name', 'category']
        verbose_name = "Subcategoria"
        verbose_name_plural = "Subcategorias"
    
    def __str__(self):
        return f"{self.category.name} > {self.name}"


class ProfessionalService(models.Model):
    """Services offered by professionals"""
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='services')
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(ServiceSubcategory, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Preço base em AOA")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['professional', 'category']
        unique_together = ['professional', 'category', 'subcategory']
        verbose_name = "Serviço do Profissional"
        verbose_name_plural = "Serviços dos Profissionais"
    
    def __str__(self):
        service_name = self.subcategory.name if self.subcategory else self.category.name
        return f"{self.professional.name} - {service_name}"


# ============================================================================
# BOOKINGS APP - models.py
# ============================================================================

class Booking(models.Model):
    """Booking model - connects clients with professionals"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmado'),
        ('in_progress', 'Em Progresso'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bookings')
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(ProfessionalService, on_delete=models.CASCADE, related_name='bookings')
    
    # Location
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.SET_NULL, null=True, blank=True)
    address_line = models.CharField(max_length=500, blank=True, null=True)
    
    # Booking details
    service_description = models.TextField()
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    special_instructions = models.TextField(blank=True, null=True)
    
    # Status and pricing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    agreed_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        indexes = [
            models.Index(fields=['status', 'scheduled_date']),
            models.Index(fields=['professional', 'status']),
        ]
    
    def __str__(self):
        return f"{self.client.name} → {self.professional.name} ({self.get_status_display()})"
    
    def can_be_reviewed(self):
        """Check if booking can be reviewed (must be completed)"""
        return self.status == 'completed'


# ============================================================================
# REVIEWS APP - models.py
# ============================================================================

class Review(models.Model):
    """Review model - linked to completed bookings only"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="Rating de 1 a 5")
    comment = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=True)  # For moderation
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
    
    def __str__(self):
        return f"Review {self.rating}★ por {self.booking.client.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update professional's average rating
        if self.booking.professional:
            self.booking.professional.update_rating()
    
    def delete(self, *args, **kwargs):
        professional = self.booking.professional
        super().delete(*args, **kwargs)
        # Recalculate rating after deletion
        if professional:
            professional.update_rating()

