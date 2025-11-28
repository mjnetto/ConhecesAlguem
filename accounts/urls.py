from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Client authentication
    path('cliente/login/', views.client_login, name='client_login'),
    path('cliente/logout/', views.client_logout, name='client_logout'),
    path('cliente/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('choose-user-type/', views.choose_user_type, name='choose_user_type'),
    path('google-callback/', views.google_oauth_callback, name='google_oauth_callback'),
    
    # Professional authentication
    path('profissional/login/', views.professional_login, name='professional_login'),
    path('profissional/logout/', views.professional_logout, name='professional_logout'),
    path('profissional/dashboard/', views.professional_dashboard, name='professional_dashboard'),
    path('profissional/reserva/<int:booking_id>/<str:action>/', views.professional_booking_action, name='professional_booking_action'),
    path('profissional/<int:pk>/', views.professional_profile, name='professional_profile'),
    path('profissional/<int:pk>/denunciar/', views.report_professional, name='report_professional'),
    
    # Professional registration
    path('registro-profissional/', views.register_professional, name='register_professional'),
    path('registro-profissional/etapa-2/', views.register_professional_step2, name='register_professional_step2'),
    path('registro-profissional/etapa-3/', views.register_professional_step3, name='register_professional_step3'),
    path('registro-profissional/portfolio/', views.register_professional_portfolio, name='register_professional_portfolio'),
    path('registro-profissional/confirmacao/<int:professional_id>/', views.register_professional_success, name='register_professional_success'),
]
