from django.core.exceptions import ValidationError
from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html
from .models import Producto, Marca, Categoria


class EstadoImagenFilter(admin.SimpleListFilter):
    title = 'Estado de imagen'
    parameter_name = 'estado_imagen'

    def lookups(self, request, model_admin):
        return (
            ('con', 'Con imagen'),
            ('sin', 'Sin imagen'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'con':
            return queryset.exclude(Q(imagen__isnull=True) | Q(imagen=''))
        if value == 'sin':
            return queryset.filter(Q(imagen__isnull=True) | Q(imagen=''))
        return queryset

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'padre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('imagen_preview', 'nombre', 'sku', 'precio', 'precio_oferta', 'volumen_ml', 'genero', 'marca', 'categoria', 'categorias_list', 'activo')
    list_filter = ('genero', 'marca', 'categoria', 'activo', EstadoImagenFilter)
    search_fields = ('nombre', 'sku', 'descripcion')
    list_editable = ('precio', 'precio_oferta', 'activo')
    readonly_fields = ('imagen_preview_large',)
    filter_horizontal = ('categorias_secundarias',)
    fieldsets = (
        (None, {
            'fields': ('nombre', 'sku', 'marca', 'categoria', 'categorias_secundarias', 'genero', 'precio', 'precio_oferta', 'volumen_ml', 'stock', 'imagen', 'imagen_preview_large', 'descripcion', 'activo')
        }),
    )

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.imagen.url)
        return "No Image"
    imagen_preview.short_description = "Imagen"

    def imagen_preview_large(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-width: 300px; border-radius: 10px;" />', obj.imagen.url)
        return "No Image"
    imagen_preview_large.short_description = "Vista Previa"

    def categorias_list(self, obj):
        secs = [c.nombre for c in obj.categorias_secundarias.all()]
        return ", ".join(secs) if secs else '-'
    categorias_list.short_description = 'Categorias secundarias'

    def save_model(self, request, obj, form, change):
        """Override save_model para validar que precio_oferta < precio antes de guardar."""
        try:
            obj.full_clean()
        except ValidationError as e:
            # Si hay un error de validación, mostrar un mensaje amigable al admin
            self.message_user(request, f"Error de validación: {e.message_dict}", level=40)  # 40 = ERROR
            return
        super().save_model(request, obj, form, change)
