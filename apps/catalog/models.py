from django.db import models
from django.contrib.auth.models import User

class Marca(models.Model):
    """Modelo de marcas de perfumes."""
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'marcas'
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
    
    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    """Modelo de categorías de productos."""
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategorias')
    
    class Meta:
        db_table = 'categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
    
    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Modelo de productos para perfumería."""
    GENERO_CHOICES = (
        ('hombre', 'Hombre'),
        ('mujer', 'Mujer'),
        ('unisex', 'Unisex'),
    )
    sku = models.CharField(max_length=50, unique=True, default='SKU-NEW')
    nombre = models.CharField(max_length=250)
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES, default='unisex')
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    volumen_ml = models.PositiveIntegerField(null=True, blank=True, help_text='Capacidad en mililitros (ml)')
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    categorias_secundarias = models.ManyToManyField(Categoria, blank=True, related_name='productos_secundarios')
    peso_kg = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    stock = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
    
    def __str__(self):
        return self.nombre
