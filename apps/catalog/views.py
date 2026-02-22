from django.shortcuts import render, get_object_or_404
import logging
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Producto, Categoria

def catalogo(request):
    """Vista que renderiza el catálogo adaptado a la perfumería."""
    productos_list = Producto.objects.filter(activo=True).select_related('marca', 'categoria').order_by('-id')
    
    # Filtrado por categoría
    categoria_id = request.GET.get('categoria')
    if categoria_id and categoria_id != 'todas':
        productos_list = productos_list.filter(categoria_id=categoria_id)

    # Filtrado por búsqueda
    query = request.GET.get('q')
    if query:
        productos_list = productos_list.filter(nombre__icontains=query)
    
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

    # Mostrar solo las categorías deseadas en el catálogo
    # Permitimos coincidencias parciales (case-insensitive) para cubrir variantes de nombres
    from django.db.models import Q
    allowed_terms = ['hombre', 'mujer', 'unisex', 'floral', 'amaderad', 'citr', 'oriental']
    q = Q()
    for t in allowed_terms:
        q |= Q(nombre__icontains=t)
    categorias = Categoria.objects.filter(q).order_by('id')
    # Debug: log sample of categorias and productos types/values to help trace rendering issue
    logger = logging.getLogger(__name__)
    try:
        logger.warning('DEBUG categorias count=%s sample=%s', categorias.count(), list(categorias.values('id','nombre')[:10]))
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
