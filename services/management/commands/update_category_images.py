"""
Comando Django para atualizar URLs de imagens e search_keywords das categorias de serviços
Execute: python manage.py update_category_images
"""
from django.core.management.base import BaseCommand
from services.models import ServiceCategory


class Command(BaseCommand):
    help = 'Atualiza URLs de imagens e search_keywords das categorias de serviços'

    # Mapeamento de slugs para URLs de imagens do Unsplash
    IMAGE_URLS = {
        'trabalhadora-domestica': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80&auto=format&fit=crop',
        'limpeza': 'https://images.unsplash.com/photo-1628177142898-93e36e4e3a50?w=800&q=80&auto=format&fit=crop',
        'montagem-moveis': 'https://images.unsplash.com/photo-1538688525198-9b88f6f53126?w=800&q=80&auto=format&fit=crop',
        'montagem-parede': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&q=80&auto=format&fit=crop',
        'reparacao-computador': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80&auto=format&fit=crop',
        'mecanico': 'https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=800&q=80&auto=format&fit=crop',
        'canalizacao': 'https://images.unsplash.com/photo-1621905251918-48416bd8575a?w=800&q=80&auto=format&fit=crop',
        'eletrico': 'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=800&q=80&auto=format&fit=crop',
        'mudancas': 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=800&q=80&auto=format&fit=crop',
    }
    
    # Mapeamento de slugs para search_keywords
    SEARCH_KEYWORDS = {
        'trabalhadora-domestica': 'Trabalhadora Doméstica, Empregada Doméstica, Serviços Domésticos, Limpeza Doméstica, Cuidados Domésticos',
        'limpeza': 'Limpeza, Limpeza Residencial, Limpeza de Escritório, Limpeza Profunda, Limpeza de Móveis',
        'montagem-moveis': 'Montagem de Móveis, IKEA, Montagem de Estantes, Montagem de Camas, Montagem de Guarda-Roupas',
        'montagem-parede': 'Montagem de TV, Montagem em Parede, Suporte de TV, Montagem de Quadros, Montagem de Prateleiras',
        'reparacao-computador': 'Reparação de Computador, Reparação de Laptop, Manutenção de PC, Formatação, Recuperação de Dados',
        'mecanico': 'Mecânico, Reparação Automóvel, Manutenção de Carros, Troca de Óleo, Reparação de Motor',
        'canalizacao': 'Canalização, Canalizador, Reparação de Torneiras, Desentupimento, Instalação Sanitária',
        'eletrico': 'Elétrico, Eletricista, Instalação Elétrica, Reparação Elétrica, Instalação de Luminárias',
        'mudancas': 'Mudanças, Mudança de Casa, Transporte de Móveis, Empresa de Mudanças, Mudança de Escritório',
    }

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🖼️  Atualizando imagens e keywords das categorias de serviços...\n'))
        
        updated_count = 0
        for slug, image_url in self.IMAGE_URLS.items():
            try:
                category = ServiceCategory.objects.get(slug=slug)
                old_url = category.icon_url
                old_keywords = category.search_keywords
                
                category.icon_url = image_url
                if slug in self.SEARCH_KEYWORDS:
                    category.search_keywords = self.SEARCH_KEYWORDS[slug]
                
                category.save()
                
                changes = []
                if old_url != image_url:
                    changes.append('imagem')
                if old_keywords != category.search_keywords:
                    changes.append('keywords')
                
                if changes:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Atualizado ({", ".join(changes)}): {category.name} ({slug})')
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'ℹ️  Já estava atualizado: {category.name} ({slug})')
                    )
            except ServiceCategory.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Categoria não encontrada: {slug}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ {updated_count} categorias atualizadas!')
        )

