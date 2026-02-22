import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django
django.setup()

from django.core.files import File
from apps.catalog.models import Marca, Categoria, Producto

m1, _ = Marca.objects.get_or_create(nombre='Tom Ford')
m2, _ = Marca.objects.get_or_create(nombre='Chanel')

# Ensure categories exist
c_hombre, _ = Categoria.objects.get_or_create(nombre='Hombre', slug='hombre')
c_mujer, _ = Categoria.objects.get_or_create(nombre='Mujer', slug='mujer')
c_unisex, _ = Categoria.objects.get_or_create(nombre='Unisex', slug='unisex')
c_floral, _ = Categoria.objects.get_or_create(nombre='Floral', slug='floral')
c_amaderado, _ = Categoria.objects.get_or_create(nombre='Amaderado', slug='amaderado')
c_citrico, _ = Categoria.objects.get_or_create(nombre='Cítrico', slug='citrico')
c_oriental, _ = Categoria.objects.get_or_create(nombre='Oriental', slug='oriental')

media_dir = BASE_DIR / 'media' / 'productos'

# Helper to attach image if exists
def attach_image(prod, filename):
    path = media_dir / filename
    if path.exists():
        with open(path, 'rb') as f:
            prod.imagen.save(filename, File(f), save=True)

# Create additional sample products
p6, created = Producto.objects.get_or_create(sku='SKU-006', defaults={'nombre':'Noir Extreme','genero':'hombre','precio':2500,'marca':m1,'categoria':c_hombre,'activo':True})
if created:
    p6.categorias_secundarias.add(c_amaderado)
    attach_image(p6, 'placeholder1.svg')

p7, created = Producto.objects.get_or_create(sku='SKU-007', defaults={'nombre':'Bleu de Chanel','genero':'hombre','precio':1800,'marca':m2,'categoria':c_hombre,'activo':True})
if created:
    p7.categorias_secundarias.add(c_citrico)
    attach_image(p7, 'placeholder2.svg')

p8, created = Producto.objects.get_or_create(sku='SKU-008', defaults={'nombre':'Chance Eau Tendre','genero':'mujer','precio':1400,'marca':m2,'categoria':c_mujer,'activo':True})
if created:
    p8.categorias_secundarias.add(c_floral)
    attach_image(p8, 'placeholder3.svg')

p9, created = Producto.objects.get_or_create(sku='SKU-009', defaults={'nombre':'Oud Wood','genero':'unisex','precio':3200,'marca':m1,'categoria':c_unisex,'activo':True})
if created:
    p9.categorias_secundarias.add(c_oriental)
    attach_image(p9, 'placeholder4.svg')

print('Seeded additional products')
