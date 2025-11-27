from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('iniciar/<int:category_id>/', views.booking_step1_service, name='step1_service'),
    path('localizacao/', views.booking_step2_location, name='step2_location'),
    path('profissionais/', views.booking_step3_professional, name='step3_professional'),
    path('confirmar/<int:professional_id>/', views.booking_confirm, name='confirm'),
    path('sucesso/<int:booking_id>/', views.booking_success, name='success'),
]

