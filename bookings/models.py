from django.db import models
from accounts.models import Client, Professional
from locations.models import Province, City, Neighborhood
from services.models import ProfessionalService


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
