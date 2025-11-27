#!/usr/bin/env python
"""
Script para regenerar fixtures com timestamps válidos para created_at
"""
import os
import sys
import django
import json
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from locations.models import Province, City, Neighborhood
from services.models import ServiceCategory

def add_timestamps_to_fixture(fixture_path, model_name):
    """Adiciona timestamps created_at e updated_at aos fixtures"""
    with open(fixture_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    base_time = timezone.now() - timedelta(days=30)  # 30 dias atrás
    
    for i, item in enumerate(data):
        if 'fields' not in item:
            continue
        
        # Remove updated_at se existir (os modelos não têm esse campo)
        if 'updated_at' in item['fields']:
            del item['fields']['updated_at']
        
        # Adiciona created_at se não existir
        if 'created_at' not in item['fields']:
            item['fields']['created_at'] = (base_time + timedelta(hours=i)).isoformat()
    
    # Salva de volta
    with open(fixture_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ {fixture_path} atualizado com timestamps")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fixtures_dir = os.path.join(base_dir, 'fixtures')
    
    fixtures = [
        ('provinces.json', 'locations.province'),
        ('luanda_cities.json', 'locations.city'),
        ('luanda_neighborhoods.json', 'locations.neighborhood'),
        ('service_categories.json', 'services.servicecategory'),
    ]
    
    for filename, model in fixtures:
        fixture_path = os.path.join(fixtures_dir, filename)
        if os.path.exists(fixture_path):
            add_timestamps_to_fixture(fixture_path, model)
        else:
            print(f"✗ {fixture_path} não encontrado")
    
    print("\n✅ Todos os fixtures foram atualizados!")

