"""
Modelos del dominio Sales - Ventas y Detalles de Venta
Migrado desde productos/models.py manteniendo:
- managed=False y PK personalizada (id_venta)  
- FK a Productos (referencia cruzada a catalog)
"""
from django.db import models
from catalog.models.products import Productos


class Ventas(models.Model):
    id_venta = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Productos, models.DO_NOTHING, db_column='id_producto')
    fecha = models.DateField()
    cantidad_vendida = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    total_venta = models.DecimalField(max_digits=23, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False  # ❌ CRÍTICO: NUNCA cambiar a True
        db_table = 'Ventas'
        
    def __str__(self):
        return f"Venta {self.id_venta} - {self.id_producto.title} ({self.fecha})"