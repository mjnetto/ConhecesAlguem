from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Review
from .forms import ReviewForm
from bookings.models import Booking
from accounts.models import Client


@require_http_methods(["GET", "POST"])
def create_review(request, booking_id):
    """Create a review for a completed booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if booking is completed
    if booking.status != 'completed':
        messages.error(request, 'Você só pode avaliar reservas concluídas.')
        return redirect('home')
    
    # Check if user is logged in as the client who made the booking
    client_id = request.session.get('client_id')
    if not client_id or client_id != booking.client.id:
        messages.warning(request, 'Por favor, faça login com o número de telefone usado na reserva para avaliar.')
        # Store booking_id in session to redirect after login
        request.session['review_booking_id'] = booking_id
        return redirect('accounts:client_login')
    
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
            # Clear review_booking_id from session if exists
            request.session.pop('review_booking_id', None)
            return redirect('accounts:professional_profile', pk=booking.professional.id)
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/create_review.html', {
        'form': form,
        'booking': booking,
        'professional': booking.professional
    })
