"""
Administración de modelos del módulo Catalog en Django Admin.
"""
from django.contrib import admin
from .models.products import Productos


@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    """Administración de Productos en Django Admin"""
    
    list_display = [
        'id_producto', 'title', 'brand', 'normal_price', 
        'oferta', 'sin_stock', 'categoria1', 'datetime'
    ]
    
    list_filter = [
        'oferta', 'sin_stock', 'categoria1', 'brand'
    ]
    
    search_fields = [
        'title', 'brand', 'categoria1', 'categoria2'
    ]
    
    readonly_fields = [
        'id_producto', 'datetime', 'ahorro', 'ahorro_percent'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('id_producto', 'title', 'brand')
        }),
        ('Precios', {
            'fields': ('normal_price', 'low_price', 'high_price')
        }),
        ('Ofertas y Descuentos', {
            'fields': ('oferta', 'ahorro', 'ahorro_percent'),
            'classes': ('collapse',)
        }),
        ('Categorización', {
            'fields': ('categoria1', 'categoria2')
        }),
        ('Estado y Stock', {
            'fields': ('sin_stock', 'kilo')
        }),
        ('Metadatos', {
            'fields': ('datetime', 'page', 'total_venta', 'Atributos'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    date_hierarchy = 'datetime'
    
    def has_add_permission(self, request):
        """
        Permitir agregar productos en desarrollo local SQLite.
        En producción con SQL Server, esto debería ser False.
        """
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar en desarrollo local"""
        return True
