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
        managed = False
        db_table = 'Productos'


class Ventas(models.Model):
    id_venta = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Productos, models.DO_NOTHING, db_column='id_producto')
    fecha = models.DateField()
    cantidad_vendida = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    total_venta = models.DecimalField(max_digits=23, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Ventas'


class StgProductosRaw(models.Model):
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
        managed = False
        db_table = 'stg_Productos_raw'