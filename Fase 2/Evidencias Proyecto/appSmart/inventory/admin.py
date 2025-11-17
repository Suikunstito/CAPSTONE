"""
Administración de modelos del módulo Inventory en Django Admin.
"""
from django.contrib import admin
from .models.movements import StgProductosRaw


@admin.register(StgProductosRaw)
class StgProductosRawAdmin(admin.ModelAdmin):
    """Administración de Staging de Productos (ETL)"""
    
    list_display = [
        'id', 'title', 'brand', 'normal_price', 
        'categoria1', 'sin_stock', 'fecha_carga'
    ]
    
    list_filter = ['sin_stock', 'fecha_carga', 'categoria1']
    
    search_fields = ['title', 'brand', 'categoria1']
    
    readonly_fields = ['id', 'fecha_carga']
    
    list_per_page = 50
    date_hierarchy = 'fecha_carga'
    
    fieldsets = (
        ('Datos Staging', {
            'fields': ('id', 'title', 'brand', 'normal_price')
        }),
        ('Categorización', {
            'fields': ('categoria1', 'sin_stock')
        }),
        ('Metadatos ETL', {
            'fields': ('fecha_carga',),
            'classes': ('collapse',)
        }),
    )
    
    def has_change_permission(self, request, obj=None):
        """Solo lectura para datos staging"""
        return False
