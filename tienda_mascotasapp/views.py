from django.shortcuts import render, redirect

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