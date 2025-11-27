from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Review
from .forms import ReviewForm
from bookings.models import Booking


@require_http_methods(["GET", "POST"])
def create_review(request, booking_id):
    """Create a review for a completed booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if booking is completed
    if booking.status != 'completed':
        messages.error(request, 'Você só pode avaliar reservas concluídas.')
        return redirect('home')
    
    # Check if review already exists
    if hasattr(booking, 'review'):
        messages.info(request, 'Você já avaliou esta reserva.')
        return redirect('accounts:professional_profile', pk=booking.professional.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()
            
            messages.success(request, 'Obrigado pela sua avaliação!')
            return redirect('accounts:professional_profile', pk=booking.professional.id)
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/create_review.html', {
        'form': form,
        'booking': booking,
        'professional': booking.professional
    })
