"""
Formularios del dominio Catalog - Productos
Migrado desde productos/forms.py (ProductoForm)
"""
from django import forms
from catalog.models.products import Productos


class ProductoForm(forms.ModelForm):
    """
    Formulario para crear/editar productos
    Excluye campos computados: datetime, page, total_venta, Atributos
    """
    class Meta:
        model = Productos
        fields = ['title', 'brand', 'normal_price', 'low_price', 'high_price',
                  'oferta', 'categoria1', 'categoria2', 'sin_stock', 'ahorro', 'ahorro_percent', 'kilo']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO(doc-sync): Aquí se podrían agregar widgets personalizados o validaciones