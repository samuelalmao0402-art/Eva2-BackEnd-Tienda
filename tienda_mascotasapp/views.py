from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Cliente
from .models import Producto
from .models import Venta
from .models import DetalleVenta
from .models import Stock

def inicio(request):
    producto = Producto.objects.all()
    cliente = Cliente.objects.all()
    return render(request, 'tienda_mascotasapp/inicio.html',{
        'producto': producto,
        'cliente': cliente,
    })

#Logica de Producto
def ingresar_producto(request):
    if request.method == 'POST':

        nombre_producto = request.POST ['Nombre_Producto']
        marca = request.POST['Marca']
        categoria = request.POST['Categoria']
        precio_costo = request.POST['Precio_Costo']
        precio_venta = request.POST['Precio_Venta']
        fecha_venc = request.POST['Fecha_Venc']

        nuevo_prod = Producto.objects.create(
            nombre_producto = nombre_producto,
            marca = marca,
            categoria = categoria,
            precio_costo = precio_costo,
            precio_venta = precio_venta,
            fecha_venc = fecha_venc if fecha_venc else None # Esto evita errores si la fecha esta vacia dandole un parametro none si el usuario se le olvida ingresar la fecha

        )
        #Crea el nuevo producto en la tabla stock de manera independiente
        Stock.objects.create(
            producto=nuevo_prod,
            stock=0,
            stock_min=1
        )
        return redirect('inicio')
    return render(request, 'tienda_mascotasapp/ingresar_prod.html')

def ver_producto(request,id):
    producto = Producto.objects.get(id=id)
    return render(request, 'tienda_mascotasapp/ver_prod.html',{'producto':producto})

def eliminar_producto(request,id):
    producto = Producto.objects.get(id=id)
    if request.method == 'POST':
        producto.delete()
        return redirect('inicio')
    return render(request, 'tienda_mascotasapp/eliminar_prod.html',{'producto':producto})

def actualizar_producto(request,id):

    producto = Producto.objects.get(id=id)
    if request.method == 'POST':
        producto.nombre_producto = request.POST ['Nombre_Producto']
        producto.marca = request.POST['Marca']
        producto.categoria = request.POST['Categoria']
        producto.precio_costo = request.POST['Precio_Costo']
        producto.precio_venta = request.POST['Precio_Venta']
        fecha_venc = request.POST['Fecha_Venc']
        producto.fecha_venc = fecha_venc if fecha_venc else None # Esto evita errores si la fecha esta vacia dandole un parametro none si el usuario se le olvida ingresar la fecha
        producto.save()
        return redirect('inicio')
    return render(request, 'tienda_mascotasapp/editar_prod.html',{'producto':producto})

# Logica de Cliente
def ingresar_cliente(request):
   
    if request.method == 'POST':
        rut = request.POST ['Rut']
        nombre = request.POST['Nombre']
        correo = request.POST['Correo']
        telefono = request.POST['Telefono']
        direccion = request.POST['Direccion']
        Cliente.objects.create(
            rut = rut,
            nombre = nombre,
            correo = correo,
            telefono = telefono,
            direccion= direccion
        )
        return redirect('inicio')
    return render(request, 'tienda_mascotasapp/ingresar_cli.html')

def ver_cliente(request,id):
    cliente = Cliente.objects.get(id=id)
    return render(request, 'tienda_mascotasapp/ver_cli.html',{'cliente': cliente})

# Logica de Stock

def ver_stock(request):
    lista_stock = Stock.objects.all()
    return render(request, 'tienda_mascotasapp/lstock.html',{'lista_stock': lista_stock})


def actualizar_stock(request, id):
    actl_stock = Stock.objects.get(id=id)
    if request.method == 'POST':
        actl_stock.stock = int(request.POST['Cantidad'])
        actl_stock.save()
        return redirect('ver_stock')
    return render(request, 'tienda_mascotasapp/actualizar_stock.html', {'stock': actl_stock})



def registrar_venta(request):
    if request.method == 'POST':
        # Capturar los datos del formulario HTML
        cliente_id = request.POST['Cliente']
        producto_id = request.POST['Producto']
        cantidad = int(request.POST['Cantidad'])
        metodo_pago = request.POST['Metodo_Pago']

        # Buscar los objetos exactos en la base de datos
        cliente_obj = Cliente.objects.get(id=cliente_id)
        producto_obj = Producto.objects.get(id=producto_id)
        stock_obj = Stock.objects.get(producto=producto_obj)

        # 0. Validar stock (¡Para que no compren más de lo que hay!)
        if cantidad > stock_obj.stock:
            # Aquí podrías mandar un mensaje de error, por ahora lo devolvemos al inicio
            return redirect('registrar_venta')

        # Calcular cuánto se va a pagar
        total_venta = producto_obj.precio_venta * cantidad

        # 1. Crear Venta (La boleta general)
        nueva_venta = Venta.objects.create(
            cliente=cliente_obj,
            total=total_venta,
            metodo_pago=metodo_pago
        )

        # 2. Crear Detalle de Venta (El producto dentro de la boleta)
        DetalleVenta.objects.create(
            venta=nueva_venta,
            producto=producto_obj,
            precio_unitario=producto_obj.precio_venta,
            cantidad=cantidad
        )

        # 3. Descontar Stock (Restarle lo que se llevó el cliente)
        stock_obj.stock -= cantidad
        stock_obj.save()

        # Enviar al usuario a la pantalla donde se ven todas las ventas
        return redirect('ver_ventas')

    # Si entra normal (sin enviar datos), le mostramos la página con las opciones
    clientes = Cliente.objects.all()
    productos = Producto.objects.all()
    return render(request, 'tienda_mascotasapp/registrar_venta.html', {
        'clientes': clientes,
        'productos': productos
    })


def ver_ventas(request):
    # Trae todas las ventas ordenadas desde la más nueva a la más vieja ('-id')
    ventas = Venta.objects.all().order_by('-id')
    return render(request, 'tienda_mascotasapp/ver_ventas.html', {'ventas': ventas})


def ver_detalle_venta(request, id):
    # Busca la venta exacta a la que se le hizo clic
    venta = Venta.objects.get(id=id)
    # Busca todos los productos que están dentro de esa venta
    detalles = DetalleVenta.objects.filter(venta=venta)
    
    return render(request, 'tienda_mascotasapp/ver_detalle_venta.html', {
        'venta': venta,
        'detalles': detalles
    })

