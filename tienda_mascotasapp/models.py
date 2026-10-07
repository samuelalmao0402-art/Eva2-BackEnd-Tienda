from django.db import models


class Venta(models.Models):
    fecha = models.DateField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE) 
    total = models.DecimalField(max_digits=30, decimal_places=2)
    metodo_pago = models.CharField(max_length=30)


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT) # Agregado: Relación con Producto
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField(default=1)
