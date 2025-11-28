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
        # Serviços Domésticos
        'trabalhadora-domestica': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80&auto=format&fit=crop',
        'limpeza': 'https://images.unsplash.com/photo-1628177142898-93e36e4e3a50?w=800&q=80&auto=format&fit=crop',
        'montagem-moveis': 'https://images.unsplash.com/photo-1538688525198-9b88f6f53126?w=800&q=80&auto=format&fit=crop',
        'montagem-parede': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&q=80&auto=format&fit=crop',
        'pintura': 'https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=800&q=80&auto=format&fit=crop',
        'jardinagem': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&q=80&auto=format&fit=crop',
        'vidraceiro': 'https://images.unsplash.com/photo-1560930950-5cc20e80e392?w=800&q=80&auto=format&fit=crop',
        'pavimentos-azulejos': 'https://images.unsplash.com/photo-1504148455328-c376907d081c?w=800&q=80&auto=format&fit=crop',
        'reparacao-portas-janelas': 'https://images.unsplash.com/photo-1519406589381-9d7c4769d4f0?w=800&q=80&auto=format&fit=crop',
        
        # Reparações e Instalações
        'reparacao-computador': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80&auto=format&fit=crop',
        'mecanico': 'https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=800&q=80&auto=format&fit=crop',
        'canalizacao': 'https://images.unsplash.com/photo-1621905251918-48416bd8575a?w=800&q=80&auto=format&fit=crop',
        'eletrico': 'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=800&q=80&auto=format&fit=crop',
        'serralharia': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&q=80&auto=format&fit=crop',
        'carpintaria': 'https://images.unsplash.com/photo-1504148455328-c376907d081c?w=800&q=80&auto=format&fit=crop',
        'instalacao-ar-condicionado': 'https://images.unsplash.com/photo-1621905252472-8af5ffc6b663?w=800&q=80&auto=format&fit=crop',
        'instalacao-eletrodomesticos': 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800&q=80&auto=format&fit=crop',
        
        # Mudanças e Transporte
        'mudancas': 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=800&q=80&auto=format&fit=crop',
        'carregamento-transporte': 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800&q=80&auto=format&fit=crop',
        'embalagem-desembalagem': 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800&q=80&auto=format&fit=crop',
        'entrega-compras': 'https://images.unsplash.com/photo-1607082349566-187342175e2f?w=800&q=80&auto=format&fit=crop',
        'remocao-lixo': 'https://images.unsplash.com/photo-1556912167-f556f1f39f7b?w=800&q=80&auto=format&fit=crop',
        
        # Serviços Digitais
        'programacao-ti': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&q=80&auto=format&fit=crop',
        'design-grafico': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800&q=80&auto=format&fit=crop',
        'marketing-digital': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80&auto=format&fit=crop',
        'influenciador': 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=800&q=80&auto=format&fit=crop',
        'fotografia-video': 'https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=800&q=80&auto=format&fit=crop',
        
        # Outros Serviços
        'assistente-pessoal': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&q=80&auto=format&fit=crop',
        'seguranca-protecao': 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&q=80&auto=format&fit=crop',
        'organizacao-eventos': 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=800&q=80&auto=format&fit=crop',
    }
    
    # Mapeamento de slugs para search_keywords
    SEARCH_KEYWORDS = {
        'trabalhadora-domestica': 'Trabalhadora Doméstica, Empregada Doméstica, Serviços Domésticos, Limpeza Doméstica, Cuidados Domésticos',
        'limpeza': 'Limpeza, Limpeza Residencial, Limpeza Profunda, Limpeza de Móveis, Limpeza de Casa',
        'montagem-moveis': 'Montagem de Móveis, Montagem de Estantes, Montagem de Camas, Montagem de Guarda-Roupas, Montagem de Armários',
        'montagem-parede': 'Montagem de TV, Montagem em Parede, Suporte de TV, Montagem de Quadros, Montagem de Prateleiras',
        'pintura': 'Pintura, Pintor, Pintura de Casas, Pintura de Paredes, Pintura Residencial',
        'jardinagem': 'Jardinagem, Jardineiro, Paisagismo, Cuidado de Jardim, Plantação, Podas',
        'vidraceiro': 'Vidraceiro, Vidros, Instalação de Vidros, Reparação de Vidros, Espelhos',
        'pavimentos-azulejos': 'Pavimentos, Azulejos, Revestimentos, Instalação de Chão, Reparação de Azulejos',
        'reparacao-portas-janelas': 'Reparação de Portas, Reparação de Janelas, Instalação de Portas, Instalação de Janelas',
        'reparacao-computador': 'Reparação de Computador, Reparação de Laptop, Manutenção de PC, Formatação, Recuperação de Dados',
        'mecanico': 'Mecânico, Reparação Automóvel, Manutenção de Carros, Troca de Óleo, Reparação de Motor',
        'canalizacao': 'Canalização, Canalizador, Reparação de Torneiras, Desentupimento, Instalação Sanitária',
        'eletrico': 'Elétrico, Eletricista, Instalação Elétrica, Reparação Elétrica, Instalação de Luminárias',
        'serralharia': 'Serralharia, Serralheiro, Portões, Portas de Ferro, Soldadura, Estruturas Metálicas',
        'carpintaria': 'Carpintaria, Carpinteiro, Marcenaria, Móveis de Madeira, Estruturas de Madeira',
        'instalacao-ar-condicionado': 'Ar Condicionado, Instalação de AC, Manutenção de Ar Condicionado, Reparação de AC',
        'instalacao-eletrodomesticos': 'Instalação de Eletrodomésticos, Instalação de Máquinas, Montagem de Aparelhos, Instalação de Fogão',
        'mudancas': 'Mudanças, Mudança de Casa, Transporte de Móveis, Empresa de Mudanças, Mudança de Residência',
        'carregamento-transporte': 'Carregamento, Transporte, Mudança de Objetos Pesados, Empilhador',
        'embalagem-desembalagem': 'Embalagem, Desembalagem, Organização de Mudança, Embalagem de Objetos',
        'entrega-compras': 'Entrega, Compras, Supermercado, Delivery, Compras de Casa',
        'remocao-lixo': 'Remoção de Lixo, Descarte, Limpeza de Quintal, Remoção de Móveis Velhos',
        'programacao-ti': 'Programador, Desenvolvimento Web, Programação, TI, Suporte Técnico, Desenvolvedor',
        'design-grafico': 'Design Gráfico, Designer, Logos, Flyers, Material Gráfico, Identidade Visual',
        'marketing-digital': 'Marketing Digital, Redes Sociais, Gestão de Instagram, Publicidade Online, Social Media',
        'influenciador': 'Influenciador, Influencer, Criação de Conteúdo, Parcerias, Promoção de Marca',
        'fotografia-video': 'Fotografia, Vídeo, Fotógrafo, Videomaker, Eventos, Casamentos',
        'assistente-pessoal': 'Assistente Pessoal, Organização, Tarefas Pessoais, Ajuda Administrativa',
        'seguranca-protecao': 'Segurança, Proteção para Bebés, Alarme, Câmeras, Proteção Infantil',
        'organizacao-eventos': 'Organização de Eventos, Festas, Casamentos, Aniversários, Planeamento',
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

