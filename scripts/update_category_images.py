#!/usr/bin/env python
"""
Script para atualizar imagens de categorias com URLs do Unsplash
Execute: python manage.py shell < scripts/update_category_images.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from services.models import ServiceCategory

# URLs do Unsplash - imagens de alta qualidade e gratuitas
# Todas com licença livre para uso comercial
UNSPLASH_IMAGES = {
    'limpeza': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80&fit=crop',
    'montagem-moveis': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&q=80&fit=crop',
    'montagem-parede': 'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=800&q=80&fit=crop',
    'canalizacao': 'https://images.unsplash.com/photo-1621905251918-48416bd8575a?w=800&q=80&fit=crop',
    'eletrico': 'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=800&q=80&fit=crop',
    'mudancas': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80&fit=crop',
}

print("🎨 Atualizando imagens de categorias com Unsplash...\n")

updated = 0
for slug, image_url in UNSPLASH_IMAGES.items():
    try:
        category = ServiceCategory.objects.get(slug=slug)
        category.icon_url = image_url
        category.save()
        print(f"✅ {category.name}: Imagem atualizada")
        updated += 1
    except ServiceCategory.DoesNotExist:
        print(f"⚠️  Categoria '{slug}' não encontrada")
    except Exception as e:
        print(f"❌ Erro ao atualizar '{slug}': {e}")

print(f"\n✨ {updated} categorias atualizadas com imagens do Unsplash!")
print("\n💡 As imagens SVG locais continuam como fallback caso a URL falhe.")
print("💡 Para reverter, deixe o campo 'icon_url' vazio no Admin Django.")


