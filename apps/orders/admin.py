from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
from .models import Pedido, DetallePedido, Pago, Carrito

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    readonly_fields = ('subtotal',)
    extra = 0

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'usuario', 'estado', 'total', 'fecha_creacion', 'acciones')
    list_filter = ('estado', 'creado_en')
    search_fields = ('numero_pedido', 'usuario__username', 'usuario__email')
    readonly_fields = ('fecha_creacion',)
    inlines = [DetallePedidoInline]
    actions = ['marcar_enviado', 'marcar_entregado']

    def fecha_creacion(self, obj):
        return obj.creado_en.strftime("%d/%m/%Y %H:%M")
    fecha_creacion.short_description = "Fecha"

    def acciones(self, obj):
        return format_html(
            '<a class="button" href="{}">Descargar PDF</a>',
            f"/admin/orders/pedido/{obj.id}/pdf/"
        )
    acciones.short_description = "Acciones"

    def marcar_enviado(self, request, queryset):
        queryset.update(estado='enviado')
    marcar_enviado.short_description = "Marcar como Enviado"

    def marcar_entregado(self, request, queryset):
        queryset.update(estado='entregado')
    marcar_entregado.short_description = "Marcar como Entregado"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:pedido_id>/pdf/', self.admin_site.admin_view(self.generar_pdf), name='pedido-pdf'),
        ]
        return custom_urls + urls

    def generar_pdf(self, request, pedido_id):
        pedido = Pedido.objects.get(id=pedido_id)
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Header
        elements.append(Paragraph(f"Comprobante de Pedido #{pedido.numero_pedido}", styles['Title']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Info Cliente
        elements.append(Paragraph(f"<b>Cliente:</b> {pedido.usuario.username}", styles['Normal']))
        elements.append(Paragraph(f"<b>Fecha:</b> {pedido.creado_en.strftime('%d/%m/%Y')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Estado:</b> {pedido.get_estado_display()}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))

        # Tabla items
        data = [['Producto', 'Cantidad', 'Precio Unitario', 'Subtotal']]
        for item in pedido.detalles.all():
            data.append([
                item.producto.nombre if item.producto else "Producto eliminado",
                str(item.cantidad),
                f"${item.precio_unitario}",
                f"${item.subtotal}"
            ])
        
        # Añadir total
        data.append(['', '', 'Total:', f"${pedido.total}"])

        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.gold),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t)

        doc.build(elements)
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('transaccion_id', 'pedido', 'metodo_pago', 'monto', 'estado', 'fecha_pago')
    list_filter = ('metodo_pago', 'estado')
    search_fields = ('transaccion_id', 'pedido__numero_pedido')
