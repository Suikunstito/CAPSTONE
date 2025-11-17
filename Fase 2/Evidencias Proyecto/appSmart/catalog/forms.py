"""
Forms del módulo Catalog - Validaciones de productos SmartERP.
"""
from django import forms
from .models.products import Productos


class ProductoForm(forms.ModelForm):
    """
    Formulario para crear/editar productos.
    Incluye validaciones personalizadas.
    """
    class Meta:
        model = Productos
        fields = [
            'title', 'brand', 'normal_price', 'low_price', 'high_price',
            'oferta', 'categoria1', 'categoria2', 'sin_stock', 
            'ahorro', 'ahorro_percent', 'kilo'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto',
                'required': True
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca del producto'
            }),
            'normal_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'low_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'high_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'oferta': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sin_stock': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'categoria1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Categoría principal'
            }),
            'categoria2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Categoría secundaria (opcional)'
            }),
            'ahorro': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'readonly': True  # Calculado automáticamente
            }),
            'ahorro_percent': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '1',
                'readonly': True  # Calculado automáticamente
            }),
            'kilo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.000',
                'step': '0.001',
                'min': '0'
            }),
        }
        labels = {
            'title': 'Nombre del Producto',
            'brand': 'Marca',
            'normal_price': 'Precio Normal',
            'low_price': 'Precio Bajo',
            'high_price': 'Precio Alto',
            'oferta': 'En Oferta',
            'sin_stock': 'Sin Stock',
            'categoria1': 'Categoría Principal',
            'categoria2': 'Categoría Secundaria',
            'ahorro': 'Ahorro ($)',
            'ahorro_percent': 'Ahorro (%)',
            'kilo': 'Peso (kg)'
        }
        help_texts = {
            'title': 'Nombre descriptivo del producto',
            'normal_price': 'Precio regular de venta',
            'low_price': 'Precio mínimo (para ofertas)',
            'high_price': 'Precio máximo (histórico)',
            'ahorro': 'Se calcula automáticamente si hay oferta',
            'ahorro_percent': 'Se calcula automáticamente si hay oferta',
            'kilo': 'Peso del producto en kilogramos'
        }
    
    def clean_normal_price(self):
        """Validar que el precio normal sea positivo"""
        price = self.cleaned_data.get('normal_price')
        if price and price < 0:
            raise forms.ValidationError('El precio no puede ser negativo')
        return price
    
    def clean_low_price(self):
        """Validar que el precio bajo sea menor al normal"""
        low_price = self.cleaned_data.get('low_price')
        normal_price = self.cleaned_data.get('normal_price')
        
        if low_price and normal_price and low_price > normal_price:
            raise forms.ValidationError(
                'El precio bajo debe ser menor al precio normal'
            )
        return low_price
    
    def clean_high_price(self):
        """Validar que el precio alto sea mayor al normal"""
        high_price = self.cleaned_data.get('high_price')
        normal_price = self.cleaned_data.get('normal_price')
        
        if high_price and normal_price and high_price < normal_price:
            raise forms.ValidationError(
                'El precio alto debe ser mayor al precio normal'
            )
        return high_price
    
    def clean(self):
        """Validaciones a nivel de formulario completo"""
        cleaned_data = super().clean()
        oferta = cleaned_data.get('oferta')
        low_price = cleaned_data.get('low_price')
        normal_price = cleaned_data.get('normal_price')
        
        # Si está en oferta, debe tener precio bajo
        if oferta and not low_price:
            self.add_error('low_price', 
                          'Debes especificar un precio bajo para productos en oferta')
        
        # Calcular ahorro automáticamente si hay oferta
        if oferta and low_price and normal_price:
            ahorro = normal_price - low_price
            ahorro_percent = int((ahorro / normal_price) * 100)
            cleaned_data['ahorro'] = ahorro
            cleaned_data['ahorro_percent'] = ahorro_percent
        else:
            cleaned_data['ahorro'] = None
            cleaned_data['ahorro_percent'] = None
        
        return cleaned_data


class ProductoSearchForm(forms.Form):
    """
    Formulario de búsqueda y filtrado de productos.
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar productos...'
        })
    )
    
    stock = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todos los estados'),
            ('disponible', 'Con Stock'),
            ('sin_stock', 'Sin Stock'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    oferta = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todas las ofertas'),
            ('true', 'En Oferta'),
            ('false', 'Sin Oferta'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    orden = forms.ChoiceField(
        required=False,
        choices=[
            ('title', 'Nombre A-Z'),
            ('-title', 'Nombre Z-A'),
            ('normal_price', 'Precio Menor'),
            ('-normal_price', 'Precio Mayor'),
            ('brand', 'Marca A-Z'),
            ('-brand', 'Marca Z-A'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
