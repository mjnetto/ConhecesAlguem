from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profissional/<int:pk>/', views.professional_profile, name='professional_profile'),
    path('registro-profissional/', views.register_professional, name='register_professional'),
    path('registro-profissional/etapa-2/', views.register_professional_step2, name='register_professional_step2'),
    path('registro-profissional/etapa-3/', views.register_professional_step3, name='register_professional_step3'),
    path('registro-profissional/portfolio/', views.register_professional_portfolio, name='register_professional_portfolio'),
    path('registro-profissional/confirmacao/<int:professional_id>/', views.register_professional_success, name='register_professional_success'),
]
