from rest_framework import serializers
from .models import Pedido, DetallePedido, Pago
from apps.catalog.serializers import ProductoSerializer

class DetallePedidoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(
        source='producto', read_only=True
    )

    class Meta:
        model = DetallePedido
        fields = ['id', 'producto', 'producto_id', 'cantidad', 'precio_unitario', 'subtotal']

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    pago = PagoSerializer(read_only=True)

    class Meta:
        model = Pedido
        fields = '__all__'
        read_only_fields = ['usuario', 'numero_pedido', 'total', 'estado', 'creado_en']

class CrearPagoSerializer(serializers.Serializer):
    pedido_id = serializers.IntegerField()
    email = serializers.EmailField()
    nombre = serializers.CharField(max_length=200)
