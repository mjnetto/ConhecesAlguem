from django.db import models


class Province(models.Model):
    """Angolan Provinces - 18 provinces"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Província"
        verbose_name_plural = "Províncias"
    
    def __str__(self):
        return self.name


class City(models.Model):
    """Cities within provinces"""
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['province', 'name']
        unique_together = ['name', 'province']
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"
    
    def __str__(self):
        return f"{self.name}, {self.province.name}"


class Neighborhood(models.Model):
    """Neighborhoods (mainly for Luanda)"""
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='neighborhoods')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['city', 'name']
        unique_together = ['name', 'city']
        verbose_name = "Bairro"
        verbose_name_plural = "Bairros"
    
    def __str__(self):
        return f"{self.name}, {self.city.name}"
