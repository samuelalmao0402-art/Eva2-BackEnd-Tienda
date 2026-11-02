from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
# Creamos la Tabla cliente para que llevar un registro de los clientes que han realizado una compra
# Consultar a tobal si le gusta ?

class Usuario(AbstractUser):
    # Campo opcional para distinguir roles visualmente si lo necesitas
    Roles = (
        ('admin', 'Administrador'),
        ('cliente', 'Cliente'),
    )
    roles = models.CharField(max_length=20, choices=Roles, default='cliente')
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # Requerido por el comando createsuperuser de Django

class Cliente(models.Model):# Separamos cliente y usuario con una relacion de uno a uno cosa de que un usuario tenga un solo perfil cliente y no muchos por ello no se uso foreinkey
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil')
    rut = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=30)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=100)

class Producto(models.Model):
    nombre_producto = models.CharField(max_length=50)
    marca = models.CharField(max_length=30)
    categoria =  models.CharField(max_length=30)
    precio_costo= models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venc = models.DateField(null=True, blank=True)
    estado = models.BooleanField(default=True)
    # Se aplica soft delete o borrado logico para eliminar desde el sitio pero se mantiene una tranzabilidad historica de las ventas de productos que han sido o requieren ser eliminados.
    #Se le asigna el estado True al realizar el borrado solo se podran visualizar los productos con estado true o activo y los inactivos se encontraran o en estado inactivo o eliminado pero sin borrar los datos de ventas.


class CarritoCompra(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    crear_at = models.DateTimeField(auto_now_add=True)# auto_now_add=True: esta funcion lo que realiza es mantener la fecha de creacion inicial cuando se crea por primera vez el carrito 

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(CarritoCompra, on_delete=models.CASCADE, related_name='items')
    # related_name='items': esta funcion le asigna un nombre a las clases hijas en relacion a las clase padre que seria carrito en vez de dejar que django le asigne un valor por defecto,
    # se le asigna un valor para mas limpieza a la hora de implementar logica
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_compra = models.PositiveIntegerField(default=1)
    # Se implemento directamente PositiveIntergerField para evitar cantidades de productos negativos en una compra 
class Stock(models.Model):
    producto= models.ForeignKey(Producto, on_delete=models.PROTECT)
    stock = models.PositiveIntegerField(default=0) # --> El parametro de default asigna por defecto una cantidad si aun no se agregan datos al stock
    stock_min= models.PositiveIntegerField(default=1)# Esto con el fin de que no se agreguen datos nulos a la tabla
    # Se cambio IntergerField por PositiveIntergerField para validar que ningun producto sea negativos 
    #ya que con interger son todos los numeros enteros entonces se puede ingresar numeros negativos 
    # si no se realiza una validacion por ende aplicamos este formato de la bd y ademas un condicional para validar 

class Venta(models.Model):
    fecha = models.DateField()
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT) 
    total = models.DecimalField(max_digits=30, decimal_places=2)
    t_metodo_pago = [
        ('Transferencia', 'TRANSFERENCIA'),
        ('Debito', 'DEBITO'),
        ('Credito', 'CREDITO')
    ] # Se aplico una tupla para poder seleccionar una opcion en vez de escribirla directamente podra selecionarla por medio de <select><options> con un desplegable en html
    metodo_pago = models.CharField(max_length=20, choices=t_metodo_pago)
    t_entrega = [
        ('Delivery', 'ENTREGA A DOMICILIO'),
        ('Presencial','RETIRO EN SUCURSAL' )
    ]
    entrega = models.CharField(max_length=20, choices=t_entrega)

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT) # Agregado: Relación con Producto
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_producto = models.PositiveIntegerField(default=1)
    # Se cambio IntergerField por PositiveIntergerField para validar que ningun producto sea negativos 
    #ya que con interger son todos los numeros enteros entonces se puede ingresar numeros negativos 
    # si no se realiza una validacion por ende aplicamos este formato de la bd y ademas un condicional para validar 


