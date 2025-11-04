"""
Modelos del dominio Catalog - Productos y Categorías
Migrado desde productos/models.py manteniendo todas las características:
- managed=False (esquema controlado externamente)
- PKs personalizadas (id_producto)
- Collation Modern_Spanish_CI_AS
"""
from django.db import models


class Productos(models.Model):
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
        managed = False  # ❌ CRÍTICO: NUNCA cambiar a True
        db_table = 'Productos'

    def __str__(self):
        return f"{self.title} - {self.brand or 'Sin marca'}"