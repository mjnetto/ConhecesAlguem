"""
Comando Django para atualizar URLs de imagens das categorias de serviços
Execute: python manage.py update_category_images
"""
from django.core.management.base import BaseCommand
from services.models import ServiceCategory


class Command(BaseCommand):
    help = 'Atualiza URLs de imagens das categorias de serviços com imagens do Unsplash'

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

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🖼️  Atualizando imagens das categorias de serviços...\n'))
        
        updated_count = 0
        for slug, image_url in self.IMAGE_URLS.items():
            try:
                category = ServiceCategory.objects.get(slug=slug)
                old_url = category.icon_url
                category.icon_url = image_url
                category.save()
                if old_url != image_url:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Atualizado: {category.name} ({slug})')
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
            self.style.SUCCESS(f'\n✅ {updated_count} categorias atualizadas com imagens do Unsplash!')
        )

