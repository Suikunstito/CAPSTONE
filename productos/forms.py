from django import forms
from .models import Productos

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ['title', 'brand', 'normal_price', 'low_price', 'high_price',
                  'oferta', 'categoria1', 'categoria2', 'sin_stock', 'ahorro', 'ahorro_percent', 'kilo']
