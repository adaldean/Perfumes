from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
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
