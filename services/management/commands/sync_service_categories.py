"""
Comando Django para sincronizar categorias de serviços do fixture com o banco de dados
Cria categorias que não existem e atualiza as que já existem
Execute: python manage.py sync_service_categories
"""
import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from services.models import ServiceCategory


class Command(BaseCommand):
    help = 'Sincroniza categorias de serviços do fixture com o banco de dados - cria as que faltam e atualiza as existentes'

    def handle(self, *args, **options):
        # Caminho para o fixture
        fixture_path = os.path.join(settings.BASE_DIR, 'fixtures', 'service_categories.json')
        
        if not os.path.exists(fixture_path):
            self.stdout.write(
                self.style.ERROR(f'❌ Fixture não encontrado: {fixture_path}')
            )
            return
        
        # Carrega o fixture
        with open(fixture_path, 'r', encoding='utf-8') as f:
            fixtures_data = json.load(f)
        
        self.stdout.write(self.style.SUCCESS('🔄 Sincronizando categorias de serviços...\n'))
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for item in fixtures_data:
            if item.get('model') != 'services.servicecategory':
                continue
            
            fields = item['fields']
            slug = fields['slug']
            
            # Verifica se a categoria já existe
            category, created = ServiceCategory.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': fields['name'],
                    'name_en': fields.get('name_en', ''),
                    'icon_url': fields.get('icon_url', ''),
                    'description': fields.get('description', ''),
                    'search_keywords': fields.get('search_keywords', ''),
                    'is_active': fields.get('is_active', True),
                    'sort_order': fields.get('sort_order', 0),
                }
            )
            
            if created:
                # Categoria criada
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Criada: {category.name} ({slug})')
                )
                created_count += 1
            else:
                # Categoria já existe - atualiza se necessário
                needs_update = False
                changes = []
                
                if category.name != fields['name']:
                    category.name = fields['name']
                    changes.append('nome')
                    needs_update = True
                
                if category.name_en != fields.get('name_en', ''):
                    category.name_en = fields.get('name_en', '')
                    changes.append('nome_en')
                    needs_update = True
                
                if category.icon_url != fields.get('icon_url', ''):
                    category.icon_url = fields.get('icon_url', '')
                    changes.append('imagem')
                    needs_update = True
                
                if category.description != fields.get('description', ''):
                    category.description = fields.get('description', '')
                    changes.append('descrição')
                    needs_update = True
                
                if category.search_keywords != fields.get('search_keywords', ''):
                    category.search_keywords = fields.get('search_keywords', '')
                    changes.append('keywords')
                    needs_update = True
                
                if category.is_active != fields.get('is_active', True):
                    category.is_active = fields.get('is_active', True)
                    changes.append('ativo')
                    needs_update = True
                
                if category.sort_order != fields.get('sort_order', 0):
                    category.sort_order = fields.get('sort_order', 0)
                    changes.append('ordem')
                    needs_update = True
                
                if needs_update:
                    category.save()
                    self.stdout.write(
                        self.style.WARNING(f'🔄 Atualizada ({", ".join(changes)}): {category.name} ({slug})')
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'ℹ️  Já atualizada: {category.name} ({slug})')
                    )
                    skipped_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Sincronização concluída!\n'
                f'   📦 Criadas: {created_count}\n'
                f'   🔄 Atualizadas: {updated_count}\n'
                f'   ℹ️  Sem alterações: {skipped_count}\n'
                f'   📊 Total no banco: {ServiceCategory.objects.count()} categorias'
            )
        )

