from django.db import models
from catalog.models.products import Productos  # Import entre apps


class Ventas(models.Model):
    """
    Modelo de ventas con relación cross-app a Productos.
    Migrado desde productos.models.Ventas manteniendo compatibilidad completa.
    """
    id_venta = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Productos, models.DO_NOTHING, db_column='id_producto')
    fecha = models.DateField()
    cantidad_vendida = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    total_venta = models.DecimalField(max_digits=23, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False  # CRÍTICO: No permitir migraciones Django
        db_table = 'Ventas'

    def __str__(self):
        return f"Venta {self.id_venta} - {self.id_producto.title if self.id_producto else 'Producto eliminado'}"

    @property
    def total_calculado(self):
        """Total calculado de la venta"""
        return self.cantidad_vendida * self.precio_unitario if self.cantidad_vendida and self.precio_unitario else 0