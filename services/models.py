from django.db import models


class ServiceCategory(models.Model):
    """Main service categories (e.g., Cleaning, Plumbing)"""
    name = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200, blank=True, null=True)  # English name
    slug = models.SlugField(unique=True)
    icon_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL externa (opcional). Se vazio, usa ícone SVG local.")
    description = models.TextField(blank=True, null=True)
    search_keywords = models.TextField(blank=True, null=True, help_text="Palavras-chave separadas por vírgula para sugestões de busca")
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Categoria de Serviço"
        verbose_name_plural = "Categorias de Serviço"
    
    def __str__(self):
        return self.name
    
    def get_icon_url(self):
        """Retorna a URL do ícone - usa imagem de alta qualidade se disponível, senão usa SVG local"""
        from django.templatetags.static import static
        
        # Se tiver URL externa (Unsplash, Pexels, etc), usa ela
        if self.icon_url and self.icon_url.strip():
            return self.icon_url
        
        # Caso contrário, usa ícone SVG local (sempre disponível)
        icon_map = {
            'limpeza': 'images/icons/cleaning.svg',
            'montagem-moveis': 'images/icons/furniture.svg',
            'montagem-parede': 'images/icons/wall-mount.svg',
            'canalizacao': 'images/icons/plumbing.svg',
            'eletrico': 'images/icons/electrical.svg',
            'mudancas': 'images/icons/moving.svg',
        }
        
        icon_path = icon_map.get(self.slug, 'images/icons/cleaning.svg')  # fallback
        return static(icon_path)


class ServiceSubcategory(models.Model):
    """Subcategories within a category (e.g., Washing Machines under Appliances)"""
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'sort_order', 'name']
        unique_together = ['name', 'category']
        verbose_name = "Subcategoria"
        verbose_name_plural = "Subcategorias"
    
    def __str__(self):
        return f"{self.category.name} > {self.name}"


class ProfessionalService(models.Model):
    """Services offered by professionals"""
    professional = models.ForeignKey('accounts.Professional', on_delete=models.CASCADE, related_name='professional_services')
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(ServiceSubcategory, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Preço base em AOA")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['professional', 'category']
        unique_together = ['professional', 'category', 'subcategory']
        verbose_name = "Serviço do Profissional"
        verbose_name_plural = "Serviços dos Profissionais"
    
    def __str__(self):
        service_name = self.subcategory.name if self.subcategory else self.category.name
        return f"{self.professional.name} - {service_name}"
