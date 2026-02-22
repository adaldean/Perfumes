from django.contrib import admin
from .models import Producto, Marca, Categoria, Pedido, DetallePedido, Pago


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    """Configuración del administrador para Marcas."""
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Configuración del administrador para Categorías."""
    list_display = ('nombre', 'slug')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Configuración del administrador para Productos."""
    list_display = ('sku', 'nombre', 'precio', 'marca', 'categoria', 'activo', 'creado_en')
    list_filter = ('activo', 'creado_en', 'marca', 'categoria')
    search_fields = ('nombre', 'sku', 'descripcion')
    readonly_fields = ('creado_en', 'actualizado_en')
    fieldsets = (
        ('Información Básica', {
            'fields': ('sku', 'nombre', 'imagen', 'descripcion')
        }),
        ('Precio y Clasificación', {
            'fields': ('precio', 'marca', 'categoria', 'peso_kg')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )


class DetallePedidoInline(admin.TabularInline):
    """Inline para los detalles de pedidos."""
    model = DetallePedido
    extra = 1
    readonly_fields = ('precio_unitario', 'subtotal')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """Configuración del administrador para Pedidos."""
    list_display = ('numero_pedido', 'usuario', 'estado', 'total', 'creado_en')
    list_filter = ('estado', 'creado_en')
    search_fields = ('numero_pedido', 'usuario__username', 'usuario__email')
    readonly_fields = ('numero_pedido', 'creado_en', 'actualizado_en')
    inlines = [DetallePedidoInline]
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('numero_pedido', 'usuario', 'estado')
        }),
        ('Información de Envío', {
            'fields': ('direccion_envio', 'telefono')
        }),
        ('Monto', {
            'fields': ('total',)
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
        ('Fechas', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    """Configuración del administrador para Detalles de Pedido."""
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('pedido__creado_en',)
    search_fields = ('pedido__numero_pedido', 'producto__nombre')
    readonly_fields = ('precio_unitario', 'subtotal')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    """Configuración del administrador para Pagos."""
    list_display = ('stripe_payment_intent_id', 'pedido', 'monto', 'estado', 'creado_en')
    list_filter = ('estado', 'creado_en')
    search_fields = ('stripe_payment_intent_id', 'pedido__numero_pedido', 'id_transaccion')
    readonly_fields = ('stripe_payment_intent_id', 'stripe_customer_id', 'id_transaccion', 'creado_en', 'actualizado_en')
    fieldsets = (
        ('Información del Pago', {
            'fields': ('pedido', 'estado', 'monto', 'moneda')
        }),
        ('Información de Stripe', {
            'fields': ('stripe_payment_intent_id', 'stripe_customer_id', 'id_transaccion', 'metodo_pago'),
        }),
        ('Detalles de Error', {
            'fields': ('razon_fallo',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
