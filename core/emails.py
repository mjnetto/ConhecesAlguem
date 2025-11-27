from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_booking_confirmation_to_client(booking):
    """Send booking confirmation email to client"""
    if not booking.client.email:
        return False
    
    subject = f'Reserva Confirmada - {booking.service.category.name}'
    
    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
    context = {
        'booking': booking,
        'client': booking.client,
        'professional': booking.professional,
        'base_url': base_url,
    }
    
    html_message = render_to_string('emails/booking_confirmation_client.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.client.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erro ao enviar email para cliente: {e}")
        return False


def send_booking_notification_to_professional(booking):
    """Send new booking notification to professional"""
    if not booking.professional.email:
        return False
    
    subject = f'Nova Reserva Recebida - {booking.service.category.name}'
    
    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
    context = {
        'booking': booking,
        'client': booking.client,
        'professional': booking.professional,
        'base_url': base_url,
    }
    
    html_message = render_to_string('emails/booking_notification_professional.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.professional.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erro ao enviar email para profissional: {e}")
        return False


def send_booking_status_update_to_client(booking, old_status):
    """Send status update email to client when booking status changes"""
    if not booking.client.email:
        return False
    
    status_messages = {
        'confirmed': 'sua reserva foi confirmada',
        'cancelled': 'sua reserva foi cancelada',
        'in_progress': 'o profissional iniciou o trabalho',
        'completed': 'o serviço foi concluído',
    }
    
    message_key = booking.status
    if message_key not in status_messages:
        return False
    
    subject = f'Atualização na Reserva #{booking.id} - {status_messages[message_key].title()}'
    
    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
    context = {
        'booking': booking,
        'client': booking.client,
        'professional': booking.professional,
        'status_message': status_messages[message_key],
        'old_status': old_status,
        'base_url': base_url,
    }
    
    html_message = render_to_string('emails/booking_status_update.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.client.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erro ao enviar email de atualização: {e}")
        return False


def send_professional_registration_notification(professional):
    """Send notification to admin when a professional registers"""
    admin_email = getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
    
    subject = f'Novo Cadastro de Profissional - {professional.name}'
    
    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
    context = {
        'professional': professional,
        'admin_url': f'{base_url}/admin/accounts/professional/{professional.id}/change/',
    }
    
    html_message = render_to_string('emails/professional_registration_admin.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erro ao enviar notificação de registro: {e}")
        return False


def send_professional_activation_email(professional):
    """Send activation confirmation email to professional"""
    if not professional.email:
        return False
    
    subject = 'Sua Conta foi Ativada - Conheces Alguém?'
    
    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
    context = {
        'professional': professional,
        'login_url': f'{base_url}/accounts/profissional/login/',
    }
    
    html_message = render_to_string('emails/professional_activation.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[professional.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erro ao enviar email de ativação: {e}")
        return False

