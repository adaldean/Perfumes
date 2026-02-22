from django.shortcuts import render, get_object_or_404
import logging
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Producto, Categoria

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
            cat = Categoria.objects.filter(nombre__icontains=key).order_by('id').first()
            if not cat:
                # fallback: normalize names and match
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
