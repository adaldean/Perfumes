from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegistroSerializer

class RegistroView(TokenObtainPairView):
    """
    Vista para registrar nuevos usuarios.
    POST /api/auth/registro/
    """
    permission_classes = [AllowAny]
    serializer_class = RegistroSerializer
    
    def post(self, request, *args, **kwargs):
        """Registrar un nuevo usuario."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Usuario registrado exitosamente',
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
        }, status=status.HTTP_201_CREATED)
