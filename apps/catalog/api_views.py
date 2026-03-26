from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum
from .models import Producto
from .serializers import ProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Productos.
    Permite: GET (listar, obtener), POST/PUT/PATCH/DELETE (solo admin/staff)
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Permitir lectura sin autenticación, escritura solo autenticados."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


@api_view(['GET'])
@permission_classes([AllowAny])
def best_sellers(request):
    """Obtiene los 8 productos más vendidos por cantidad"""
    productos = Producto.objects.filter(activo=True).annotate(
        total_vendido=Sum('detallepedido__cantidad')
    ).order_by('-total_vendido')[:8]
    serializer = ProductoSerializer(productos, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def productos_por_genero(request, genero):
    """Obtiene productos filtrados por género (mujer, hombre, unisex)"""
    genero = genero.lower()
    if genero not in ['mujer', 'hombre', 'unisex']:
        return Response({'error': 'Género no válido'}, status=400)
    
    productos = Producto.objects.filter(genero=genero, activo=True)[:12]
    serializer = ProductoSerializer(productos, many=True, context={'request': request})
    return Response(serializer.data)
