from django.contrib import admin
from django.utils.html import format_html
from .models import Producto, Marca, Categoria

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
    list_display = ('imagen_preview', 'nombre', 'sku', 'precio', 'genero', 'marca', 'categoria', 'categorias_list', 'activo')
    list_filter = ('genero', 'marca', 'categoria', 'activo')
    search_fields = ('nombre', 'sku', 'descripcion')
    list_editable = ('precio', 'activo')
    readonly_fields = ('imagen_preview_large',)
    filter_horizontal = ('categorias_secundarias',)
    fieldsets = (
        (None, {
            'fields': ('nombre', 'sku', 'marca', 'categoria', 'categorias_secundarias', 'genero', 'precio', 'stock', 'imagen', 'imagen_preview_large', 'descripcion', 'activo')
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
