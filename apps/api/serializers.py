from rest_framework import serializers
from .models import Producto, Marca, Categoria, Pedido, DetallePedido, Pago
from django.contrib.auth.models import User


class MarcaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Marca."""
    
    class Meta:
        model = Marca
        fields = ['id', 'nombre', 'descripcion']


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Categoria."""
    
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'slug', 'descripcion']


class ProductoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Producto."""
    marca = MarcaSerializer(read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    
    class Meta:
        model = Producto
        fields = ['id', 'sku', 'nombre', 'descripcion', 'precio', 'imagen', 'marca', 'categoria', 'peso_kg', 'activo', 'creado_en', 'actualizado_en']
        read_only_fields = ['id', 'creado_en', 'actualizado_en']


# ============================================
# Serializadores de Autenticación
# ============================================

class RegistroSerializer(serializers.ModelSerializer):
    """Serializador para registrar nuevos usuarios."""
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']
    
    def validate(self, data):
        """Validar que las contraseñas coincidan."""
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return data
    
    def create(self, validated_data):
        """Crear un nuevo usuario."""
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializador para el modelo User."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


# ============================================
# Serializadores de Pedidos y Pagos
# ============================================

class DetallePedidoSerializer(serializers.ModelSerializer):
    """Serializador para detalles de pedidos."""
    producto = ProductoSerializer(read_only=True)
    
    class Meta:
        model = DetallePedido
        fields = ['id', 'producto', 'cantidad', 'precio_unitario', 'subtotal']


class PedidoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Pedido."""
    usuario = UsuarioSerializer(read_only=True)
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pedido
        fields = ['id', 'usuario', 'numero_pedido', 'estado', 'total', 'direccion_envio', 'telefono', 'notas', 'detalles', 'creado_en', 'actualizado_en']
        read_only_fields = ['id', 'numero_pedido', 'creado_en', 'actualizado_en']


class PagoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Pago."""
    pedido = PedidoSerializer(read_only=True)
    
    class Meta:
        model = Pago
        fields = ['id', 'pedido', 'stripe_payment_intent_id', 'stripe_customer_id', 'monto', 'moneda', 'estado', 'metodo_pago', 'id_transaccion', 'razon_fallo', 'creado_en', 'actualizado_en']
        read_only_fields = ['id', 'stripe_payment_intent_id', 'stripe_customer_id', 'id_transaccion', 'creado_en', 'actualizado_en']


class CrearPagoSerializer(serializers.Serializer):
    """Serializador para crear un PaymentIntent en Stripe."""
    pedido_id = serializers.IntegerField()
    email = serializers.EmailField()
    nombre = serializers.CharField(max_length=255)
    
    class Meta:
        fields = ['pedido_id', 'email', 'nombre']
