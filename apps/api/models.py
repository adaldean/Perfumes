from django.db import models
from django.contrib.auth.models import User

class Marca(models.Model):
    """Modelo de marcas de perfumes."""
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'marcas'
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
    
    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    """Modelo de categorías de productos."""
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategorias')
    
    class Meta:
        db_table = 'categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
    
    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Modelo de productos para perfumería."""
    sku = models.CharField(max_length=50, unique=True, default='SKU-NEW')
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    peso_kg = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-creado_en']
    
    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    """Modelo de pedidos de clientes."""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    numero_pedido = models.CharField(max_length=50, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    direccion_envio = models.TextField()
    telefono = models.CharField(max_length=20)
    notas = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pedidos'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-creado_en']
    
    def __str__(self):
        return f"Pedido {self.numero_pedido}"


class DetallePedido(models.Model):
    """Modelo para los detalles de cada pedido."""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'detalles_pedidos'
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'
    
    def __str__(self):
        return f"Detalle del Pedido {self.pedido.numero_pedido}"


class Pago(models.Model):
    """Modelo para gestionar pagos con Stripe."""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('exitoso', 'Exitoso'),
        ('fallido', 'Fallido'),
        ('cancelado', 'Cancelado'),
    ]
    
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='pago')
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=3, default='USD')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    metodo_pago = models.CharField(max_length=50, null=True, blank=True)
    id_transaccion = models.CharField(max_length=255, unique=True, null=True, blank=True)
    razon_fallo = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pagos'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-creado_en']
    
    def __str__(self):
        return f"Pago {self.stripe_payment_intent_id} - {self.estado}"


class Carrito(models.Model):
    """
    Modelo para guardar carritos persistentes de usuarios autenticados.
    Los anónimos usan sesión (request.session).
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrito')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carritos'
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
    
    def __str__(self):
        return f"Carrito de {self.usuario.username}"
    
    @property
    def total(self):
        """Calcula el total del carrito."""
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def cantidad_items(self):
        """Cantidad total de items en el carrito."""
        return sum(item.cantidad for item in self.items.all())


class ItemCarrito(models.Model):
    """Items individuales en el carrito de un usuario."""
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1, help_text="Cantidad del producto")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'items_carrito'
        verbose_name = 'Item de Carrito'
        verbose_name_plural = 'Items de Carrito'
        unique_together = ('carrito', 'producto')  # Un producto una sola vez por carrito
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
    
    @property
    def subtotal(self):
        """Calcula el subtotal de este item."""
        return self.producto.precio * self.cantidad
