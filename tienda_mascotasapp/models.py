from django.db import models
# Create your models here.
# Creamos la Tabla cliente para que llevar un registro de los clientes que han realizado una compra
class Cliente(models.Model):
   rut = models.CharField(max_length=10)
   nombre = models.CharField(max_length=30)
   correo = models.EmailField(max_length=60)
   telefono = models.CharField(max_length=20)
   direccion = models.CharField(max_length=100)
   
class Producto(models.Model):
      nombre_producto = models.CharField(max_length=50)
      marca = models.CharField(max_length=30)
      categoría =  models.CharField(max_length=30)
      precio_costo= models.DecimalField(max_digits=10, decimal_places=2)
      precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
      fecha_venc = models.DateField()
     
class Stock(models.Model):
    producto= models.ForeignKey(Producto, models.PROTECT)
    stock = models.IntegerField(default=0) # --> El parametro de default asigna por defecto una cantidad si aun no se agregan datos al stock
    stock_min= models.IntegerField(default=1)# Esto con el fin de que no se agreguen datos nulos a la tabla





