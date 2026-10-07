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

def actulizar_stock(request, id):
    actl_stock = Stock.objects.get(id=id)
    if request.method == 'POST':
        actl_stock.stock = request.POST['Cantidad']
        actl_stock.save()
        return redirect('ver_stock')
    return render(request, 'tienda_mascotasapp/actualizar_stock.html', {'stock': actl_stock})




