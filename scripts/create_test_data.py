"""
Script para criar dados de teste (profissionais de exemplo)
Execute com: python manage.py shell < scripts/create_test_data.py
Ou: python manage.py shell -c "$(cat scripts/create_test_data.py)"
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import Professional, Client
from locations.models import Province, City
from services.models import ServiceCategory, ProfessionalService
from phonenumber_field.phonenumber import PhoneNumber

# Get Luanda province
luanda_province = Province.objects.get(name="Luanda")
luanda_city = City.objects.get(name="Luanda", province=luanda_province)

# Get service categories
categories = {
    'limpeza': ServiceCategory.objects.get(slug='limpeza'),
    'montagem-moveis': ServiceCategory.objects.get(slug='montagem-moveis'),
    'canalizacao': ServiceCategory.objects.get(slug='canalizacao'),
    'eletrico': ServiceCategory.objects.get(slug='eletrico'),
    'mudancas': ServiceCategory.objects.get(slug='mudancas'),
    'montagem-parede': ServiceCategory.objects.get(slug='montagem-parede'),
}

# Professional data
professionals_data = [
    {
        'name': 'Maria Santos',
        'phone': '+244912345678',
        'email': 'maria.santos@example.com',
        'nif': '123456789LA045',
        'iban': 'AO06004400012345678910144',
        'bio': 'Profissional experiente em limpeza residencial e comercial. Trabalho há mais de 5 anos na área.',
        'categories': ['limpeza'],
        'provinces': [luanda_province],
        'average_rating': 4.8,
        'completed_bookings': 25,
    },
    {
        'name': 'João Silva',
        'phone': '+244923456789',
        'email': 'joao.silva@example.com',
        'nif': '987654321LA045',
        'iban': 'AO06004400098765432110144',
        'bio': 'Especialista em montagem de móveis e instalação de objetos na parede. Ferramentas próprias e experiência comprovada.',
        'categories': ['montagem-moveis', 'montagem-parede'],
        'provinces': [luanda_province],
        'average_rating': 4.9,
        'completed_bookings': 42,
    },
    {
        'name': 'Carlos Mendes',
        'phone': '+244934567890',
        'email': 'carlos.mendes@example.com',
        'nif': '456789123LA045',
        'iban': 'AO06004400045678912310144',
        'bio': 'Canalizador profissional com mais de 10 anos de experiência. Atendo emergências e reparações gerais.',
        'categories': ['canalizacao'],
        'provinces': [luanda_province],
        'average_rating': 4.7,
        'completed_bookings': 38,
    },
    {
        'name': 'Ana Costa',
        'phone': '+244945678901',
        'email': 'ana.costa@example.com',
        'nif': '789123456LA045',
        'iban': 'AO06004400078912345610144',
        'bio': 'Eletricista qualificada. Reparações, instalações elétricas e manutenção. Certificada e com seguro.',
        'categories': ['eletrico'],
        'provinces': [luanda_province],
        'average_rating': 5.0,
        'completed_bookings': 55,
    },
    {
        'name': 'Pedro Alves',
        'phone': '+244956789012',
        'email': 'pedro.alves@example.com',
        'nif': '321654987LA045',
        'iban': 'AO06004400032165498710144',
        'bio': 'Serviço completo de mudanças. Equipe profissional, veículo próprio e cuidadoso com seus pertences.',
        'categories': ['mudancas'],
        'provinces': [luanda_province],
        'average_rating': 4.6,
        'completed_bookings': 18,
    },
]

print("🏗️  Criando profissionais de teste...\n")

for data in professionals_data:
    phone_number = PhoneNumber.from_string(data['phone'], region='AO')
    
    # Create or get professional
    professional, created = Professional.objects.get_or_create(
        phone_number=phone_number,
        defaults={
            'name': data['name'],
            'email': data['email'],
            'nif': data['nif'],
            'iban': data['iban'],
            'bio': data['bio'],
            'is_activated': True,
            'average_rating': data['average_rating'],
            'completed_bookings': data['completed_bookings'],
        }
    )
    
    if not created:
        # Update existing
        professional.name = data['name']
        professional.email = data['email']
        professional.bio = data['bio']
        professional.is_activated = True
        professional.average_rating = data['average_rating']
        professional.completed_bookings = data['completed_bookings']
        professional.save()
    
    # Add provinces
    professional.service_provinces.set(data['provinces'])
    
    # Create professional services
    for category_slug in data['categories']:
        category = categories[category_slug]
        ProfessionalService.objects.get_or_create(
            professional=professional,
            category=category,
            defaults={
                'description': f'Serviço de {category.name}',
                'is_active': True,
            }
        )
    
    status = "✅ Criado" if created else "🔄 Atualizado"
    print(f"{status}: {professional.name} ({category_slug})")

print(f"\n✅ Total de profissionais: {Professional.objects.filter(is_activated=True).count()}")
print(f"✅ Total de serviços cadastrados: {ProfessionalService.objects.filter(is_active=True).count()}")

