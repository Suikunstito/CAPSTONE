"""
Administración de modelos del módulo Sales en Django Admin.
"""
from django.contrib import admin
from .models.sales import Ventas


@admin.register(Ventas)
class VentasAdmin(admin.ModelAdmin):
    """Administración de Ventas en Django Admin"""
    
    list_display = [
        'id_venta', 'get_producto_title', 'cantidad_vendida', 
        'precio_unitario', 'total_venta', 'fecha'
    ]
    
    list_filter = ['fecha']
    
    search_fields = ['id_producto__title']
    
    readonly_fields = ['id_venta', 'fecha', 'total_venta']
    
    autocomplete_fields = ['id_producto']
    
    fieldsets = (
        ('Información de Venta', {
            'fields': ('id_venta', 'id_producto', 'fecha')
        }),
        ('Detalles', {
            'fields': ('cantidad_vendida', 'precio_unitario', 'total_venta')
        }),
    )
    
    list_per_page = 25
    date_hierarchy = 'fecha'
    
    def get_producto_title(self, obj):
        """Mostrar título del producto en la lista"""
        return obj.id_producto.title if obj.id_producto else '-'
    get_producto_title.short_description = 'Producto'
    get_producto_title.admin_order_field = 'id_producto__title'
    
    def save_model(self, request, obj, form, change):
        """Calcular total_venta automáticamente"""
        if obj.cantidad_vendida and obj.precio_unitario:
            obj.total_venta = obj.cantidad_vendida * obj.precio_unitario
        super().save_model(request, obj, form, change)
