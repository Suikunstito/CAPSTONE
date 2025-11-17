from django.db import models


class Productos(models.Model):
    """
    Modelo principal de productos para el catálogo.
    Migrado desde productos.models.Productos manteniendo compatibilidad completa.
    """
    id_producto = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, db_collation='Modern_Spanish_CI_AS')
    brand = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    normal_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    low_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    high_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    oferta = models.BooleanField(blank=True, null=True)
    categoria1 = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    categoria2 = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    datetime = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    atributos = models.CharField(db_column='Atributos', max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)  # Field name made lowercase.
    sin_stock = models.BooleanField(blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)
    ahorro = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    ahorro_percent = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True)
    kilo = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False  # CRÍTICO: No permitir migraciones Django
        db_table = 'Productos'

    def __str__(self):
        return f"{self.title} - {self.brand or 'Sin marca'}"

    @property
    def precio_referencia(self):
        """Precio de referencia para cálculos (prioriza normal_price)"""
        return self.normal_price or self.low_price or self.high_price or 0

    @property
    def disponible(self):
        """Producto está disponible si tiene precio y no está sin stock"""
        tiene_precio = any([self.normal_price, self.low_price, self.high_price])
        return tiene_precio and not self.sin_stock

    @property 
    def oferta_activa(self):
        """Determina si el producto está en oferta activa"""
        return bool(self.oferta) or bool(self.ahorro) or bool(self.ahorro_percent)