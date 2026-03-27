from django.shortcuts import render, get_object_or_404
import logging
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Producto, Categoria
from django.http import JsonResponse

def catalogo(request):
    """Vista que renderiza el catálogo adaptado a la perfumería."""
    productos_list = Producto.objects.filter(activo=True).select_related('marca', 'categoria').prefetch_related('categorias_secundarias').order_by('-id')
    
    # Filtrado por categoría: aceptamos tanto IDs como claves como 'hombre','mujer', etc.
    categoria_param = request.GET.get('categoria')
    if categoria_param and categoria_param != 'todas':
        # soporte para filtros de género (hombre/mujer/unisex)
        genero_keys = {'hombre', 'mujer', 'unisex'}
        if categoria_param in genero_keys:
            productos_list = productos_list.filter(genero=categoria_param)
        elif categoria_param.isdigit():
            # Si se pasó un id numérico, buscar la categoría y filtrar tanto por
            # categoría principal como por categorías secundarias.
            try:
                cat_by_id = Categoria.objects.filter(id=int(categoria_param)).first()
            except (ValueError, TypeError):
                cat_by_id = None
            if cat_by_id:
                productos_list = productos_list.filter(Q(categoria=cat_by_id) | Q(categorias_secundarias=cat_by_id))
            else:
                productos_list = productos_list.filter(categoria_id=categoria_param)
        else:
            # mapear clave textual a una categoría existente por slug o coincidencia parcial
            cat_match = Categoria.objects.filter(slug__iexact=categoria_param).order_by('id').first()
            if not cat_match:
                cat_match = Categoria.objects.filter(nombre__icontains=categoria_param).order_by('id').first()
            if cat_match:
                # incluir productos cuya categoria principal sea la buscada o que tengan la categoria en las secundarias
                productos_list = productos_list.filter(Q(categoria=cat_match) | Q(categorias_secundarias=cat_match))
            else:
                # Fallback: buscar directamente en los nombres/slugs de las categorías principales o secundarias
                productos_list = productos_list.filter(
                    Q(categoria__slug__iexact=categoria_param) |
                    Q(categoria__nombre__icontains=categoria_param) |
                    Q(categorias_secundarias__slug__iexact=categoria_param) |
                    Q(categorias_secundarias__nombre__icontains=categoria_param)
                )

    # Filtrado por búsqueda
    query = request.GET.get('q')
    if query:
        productos_list = productos_list.filter(nombre__icontains=query)
    
    # Evitar duplicados cuando se usan relaciones ManyToMany en filtros
    productos_list = productos_list.distinct()
    # (removed temporary debug logging)
    paginator = Paginator(productos_list, 12)  # Mostrar 12 productos por página
    page = request.GET.get('page')
    
    try:
        productos = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, mostrar la primera página.
        productos = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página de resultados.
        productos = paginator.page(paginator.num_pages)

    # Usar un conjunto fijo y ordenado de etiquetas para los filtros del catálogo
    fixed = [
        ('todas', 'Todos'),
        ('hombre', 'Hombre'),
        ('mujer', 'Mujer'),
        ('unisex', 'Unisex'),
        ('floral', 'Floral'),
        ('amaderado', 'Amaderado'),
        ('citrico', 'Cítrico'),
        ('oriental', 'Oriental'),
    ]

    # Construir lista de diccionarios con keys `id` y `nombre` para mantener compatibilidad con la plantilla
    categorias = []
    import unicodedata
    def _norm(s):
        if not s:
            return ''
        return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii').lower()

    for key, label in fixed:
        if key == 'todas':
            categorias.append({'id': 'todas', 'nombre': label})
        else:
            # Prefer exact matches by slug or name, fallback to contains or normalized match
            cat = Categoria.objects.filter(slug__iexact=key).first()
            if not cat:
                cat = Categoria.objects.filter(nombre__iexact=key).first()
            if not cat:
                cat = Categoria.objects.filter(nombre__icontains=key).order_by('id').first()
            if not cat:
                key_norm = _norm(key)
                for c in Categoria.objects.all():
                    if key_norm in _norm(c.nombre):
                        cat = c
                        break
            categorias.append({'id': cat.id if cat else key, 'nombre': label})

    # Debug: log sample de categorias y productos para ayudar a depurar
    logger = logging.getLogger(__name__)
    try:
        logger.warning('DEBUG categorias count=%s sample=%s', len(categorias), [c['nombre'] for c in categorias[:10]])
    except Exception as e:
        logger.exception('Error logging categorias: %s', e)
    context = {
        'productos': productos,
        'categorias': categorias,
        'busqueda': query if query else ''
    }
    return render(request, 'catalogo.html', context)

def detalle_producto(request, producto_id):
    """Vista detalle de producto."""
    producto = get_object_or_404(Producto, id=producto_id)
    # Productos relacionados (misma categoría, excluyendo el actual)
    relacionados = Producto.objects.filter(categoria=producto.categoria, activo=True).exclude(id=producto.id)[:4]
    
    context = {
        'producto': producto,
        'relacionados': relacionados
    }
    return render(request, 'catalogo/detalle.html', context)


def api_productos_por_genero(request, genero_param):
    """
    API que retorna productos filtrados por género.
    """
    productos_list = Producto.objects.filter(activo=True, genero=genero_param).select_related('marca', 'categoria').prefetch_related('categorias_secundarias').order_by('-id')
    
    products_data = []
    for producto in productos_list[:8]: # Limitar a 8 productos para la visualización del chatbot
        products_data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': float(producto.precio_oferta if producto.precio_oferta else producto.precio),
            'imagen': producto.imagen.url if producto.imagen else '/static/img/placeholder.jpg', # Asumiendo un placeholder por defecto
            'marca': producto.marca.nombre if producto.marca else '',
            'genero': producto.get_genero_display(),
            'categoria_principal': producto.categoria.nombre if producto.categoria else '',
            'categorias_secundarias': [c.nombre for c in producto.categorias_secundarias.all()]
        })
    return JsonResponse(products_data, safe=False)


def api_productos_por_categoria(request, categoria_param):
    """
    API que retorna productos filtrados por categoría (nombre o slug).
    """
    productos_list = Producto.objects.filter(activo=True).select_related('marca', 'categoria').prefetch_related('categorias_secundarias').order_by('-id')

    # Construir un objeto Q para filtrar por categorías principales o secundarias
    category_filter = Q(categoria__slug__iexact=categoria_param) | \
                      Q(categoria__nombre__iexact=categoria_param) | \
                      Q(categorias_secundarias__slug__iexact=categoria_param) | \
                      Q(categorias_secundarias__nombre__iexact=categoria_param)
    
    productos_list = productos_list.filter(category_filter).distinct()

    products_data = []
    for producto in productos_list[:8]: # Limitar a 8 productos para la visualización del chatbot
        products_data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': float(producto.precio_oferta if producto.precio_oferta else producto.precio),
            'imagen': producto.imagen.url if producto.imagen else '/static/img/placeholder.jpg', # Asumiendo un placeholder por defecto
            'marca': producto.marca.nombre if producto.marca else '',
            'genero': producto.get_genero_display(),
            'categoria_principal': producto.categoria.nombre if producto.categoria else '',
            'categorias_secundarias': [c.nombre for c in producto.categorias_secundarias.all()]
        })
    
    return JsonResponse(products_data, safe=False)


def api_best_sellers(request):
    """
    API que retorna los productos más vendidos.
    (Placeholder: actualmente retorna los 8 productos más recientes)
    Para una implementación real, se necesitaría un modelo de ventas/pedidos
    para calcular los más vendidos.
    """
    # Placeholder: Retorna los 8 productos más recientes como "best sellers"
    # En una implementación real, esto se basaría en datos de ventas.
    productos_list = Producto.objects.filter(activo=True).order_by('-creado_en')[:8] # O por conteo de ventas
    
    products_data = []
    for producto in productos_list:
        products_data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': float(producto.precio_oferta if producto.precio_oferta else producto.precio),
            'imagen': producto.imagen.url if producto.imagen else '/static/img/placeholder.jpg',
            'marca': producto.marca.nombre if producto.marca else '',
            'genero': producto.get_genero_display(),
            'categoria_principal': producto.categoria.nombre if producto.categoria else '',
            'categorias_secundarias': [c.nombre for c in producto.categorias_secundarias.all()]
        })
    return JsonResponse(products_data, safe=False)
