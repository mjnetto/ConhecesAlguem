from django.db import models
from bookings.models import Booking


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
