from django.db import models


class StgProductosRaw(models.Model):
    """
    Modelo de staging para ETL de productos (datos sin procesar).
    Migrado desde productos.models.StgProductosRaw para procesos de inventario.
    """
    title = models.TextField(db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    brand = models.CharField(max_length=4000, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    normal_price = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    low_price = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    high_price = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    oferta = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    categoria1 = models.CharField(max_length=4000, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    categoria2 = models.CharField(max_length=4000, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    datetime = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    atributos = models.CharField(db_column='Atributos', max_length=4000, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)  # Field name made lowercase.
    sin_stock = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    page = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    ahorro = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    ahorro_percent = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    kilo = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)

    class Meta:
        managed = False  # CRÍTICO: No permitir migraciones Django
        db_table = 'stg_Productos_raw'

    def __str__(self):
        return f"Raw: {self.title or 'Sin título'} - {self.brand or 'Sin marca'}"