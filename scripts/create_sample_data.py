import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django
django.setup()

from apps.catalog.models import Marca, Categoria, Producto

m1, _ = Marca.objects.get_or_create(nombre='Maison Francis Kurkdjian')
m2, _ = Marca.objects.get_or_create(nombre='Le Labo')

c_hombre, _ = Categoria.objects.get_or_create(nombre='Hombre', slug='hombre')
c_mujer, _ = Categoria.objects.get_or_create(nombre='Mujer', slug='mujer')
c_unisex, _ = Categoria.objects.get_or_create(nombre='Unisex', slug='unisex')
c_floral, _ = Categoria.objects.get_or_create(nombre='Floral', slug='floral')
c_amaderado, _ = Categoria.objects.get_or_create(nombre='Amaderado', slug='amaderado')
c_citrico, _ = Categoria.objects.get_or_create(nombre='Cítrico', slug='citrico')
c_oriental, _ = Categoria.objects.get_or_create(nombre='Oriental', slug='oriental')

p1, created = Producto.objects.get_or_create(sku='SKU-001', defaults={
    'nombre':'Baccarat Rouge 540', 'genero':'hombre', 'precio':9800, 'marca':m1, 'categoria':c_hombre, 'activo':True
})
if created:
    p1.categorias_secundarias.add(c_floral)

p2, created = Producto.objects.get_or_create(sku='SKU-002', defaults={
    'nombre':'Santal 33', 'genero':'unisex', 'precio':9800, 'marca':m2, 'categoria':c_unisex, 'activo':True
})
if created:
    p2.categorias_secundarias.add(c_amaderado)

p3, created = Producto.objects.get_or_create(sku='SKU-003', defaults={
    'nombre':'Daisy', 'genero':'mujer', 'precio':1200, 'marca':m2, 'categoria':c_mujer, 'activo':True
})
if created:
    p3.categorias_secundarias.add(c_floral)

p4, created = Producto.objects.get_or_create(sku='SKU-004', defaults={
    'nombre':'Citrus Blend', 'genero':'unisex', 'precio':450, 'marca':m1, 'categoria':c_unisex, 'activo':True
})
if created:
    p4.categorias_secundarias.add(c_citrico)

p5, created = Producto.objects.get_or_create(sku='SKU-005', defaults={
    'nombre':'Oriental Night', 'genero':'mujer', 'precio':2200, 'marca':m1, 'categoria':c_mujer, 'activo':True
})
if created:
    p5.categorias_secundarias.add(c_oriental)

print('Sample data created or already present')
