#Importacion de frameworws de seguridad para django e implmentacion de APIs e implementacion del metodo GET,POST,PUT,DELETE
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
# Importacion de funciones en models 
from .models import Cliente
from .models import Producto
from .models import Venta
from .models import DetalleVenta
from .models import Stock


def login(request):
    return render(request,'tienda_mascotasapp/login.html')


def inicio(request):
    producto = Producto.objects.all()
    cliente = Cliente.objects.all()
    return render(request, 'tienda_mascotasapp/inicio.html',{
        'producto': producto,
        'cliente': cliente,
    })

#Logica de Producto
def ingresar_producto(request):
    return render(request, 'tienda_mascotasapp/ingresar_prod.html')
        
def ver_producto(request,id):
    return render(request, 'tienda_mascotasapp/ver_prod.html')

def eliminar_producto(request,id):
    return render(request, 'tienda_mascotasapp/eliminar_prod.html')

def actualizar_producto(request):
    return render(request, 'tienda_mascotasapp/editar_prod.html')

# Logica de Cliente
def ingresar_cliente(request):
   
    if request.method == 'POST':
        rut = request.POST ['Rut']
        nombre = request.POST['Nombre']
        correo = request.POST['Correo']
        telefono = request.POST['Telefono']
        direccion = request.POST['Direccion']

        if Cliente.objects.filter(rut=rut).exists():
            # Si existe, recargamos la página enviando un mensaje de error
            return render(request, 'tienda_mascotasapp/ingresar_cli.html', {
                'error': f'¡El RUT {rut} ya está registrado en el sistema!'
            })
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
    return render(request, 'tienda_mascotasapp/ver_cli.html')

# Logica de Stock

def ver_stock(request):
    return render(request, 'tienda_mascotasapp/lstock.html')


def actualizar_stock(request, id):
    return render(request, 'tienda_mascotasapp/actualizar_stock.html')



def registrar_venta(request):
    if request.method == 'POST':
        # Capturar los datos del formulario HTML (Ajustado a los name del HTML)
        fecha = request.POST.get('fecha')
        cliente_id = request.POST.get('cliente_id')
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad'))
        metodo_pago = request.POST.get('metodo_pago')

        # Buscar los objetos exactos en la base de datos
        cliente_obj = Cliente.objects.get(id=cliente_id)
        producto_obj = Producto.objects.get(id=producto_id)
        stock_obj = Stock.objects.get(producto=producto_obj)

        # 0. Validar stock (¡Para que no compren más de lo que hay!)
        if cantidad > stock_obj.stock:
            # En vez de redirigir, mostramos el cuadro rojo de error que pusimos en el HTML
            return render(request, 'tienda_mascotasapp/registrar_venta.html', {
                'error': f'¡Stock insuficiente! Solo quedan {stock_obj.stock} unidades de {producto_obj.nombre_producto}.',
                'clientes': Cliente.objects.all(),
                'productos': Producto.objects.all()
            })

        # Calcular cuánto se va a pagar
        total_venta = producto_obj.precio_venta * cantidad

        # 1. Crear Venta (La boleta general) agregando la fecha
        nueva_venta = Venta.objects.create(
            fecha=fecha,
            cliente=cliente_obj,
            total=total_venta,
            metodo_pago=metodo_pago
        )

        # 2. Crear DetalleVenta (El registro del producto específico)
        DetalleVenta.objects.create(
            venta=nueva_venta,
            producto=producto_obj,
            precio_unitario=producto_obj.precio_venta,
            cantidad=cantidad
        )

        # 3. Descontar el stock vendido de la bodega y guardar el cambio
        stock_obj.stock -= cantidad
        stock_obj.save()

        # Al terminar, volvemos al inicio
        return redirect('inicio')

    # 4. Si entramos a la página (GET), enviamos las listas para rellenar los selectores
    return render(request, 'tienda_mascotasapp/registrar_venta.html', {
        'clientes': Cliente.objects.all(),
        'productos': Producto.objects.all()
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

#LOGICA DE NEGOCIO Y APIS APLICADAS

#APIS LOGIN --> REUTILIZAR LA DEL PROFE


# FUNCIONES GENERALES DE ADIM CON APIS 


#APIS PRODUCTOS PARA ADMIN 

class ProductosApiView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    #GET PARA MOSTRAR TODOS LOS PRODCUTOS CON ALL
    def get(self,request):

        productos = Producto.objects.all().order_by('-nombre_producto')

        productos_datos = []

        for producto in productos:

            productos_datos.append({

                'id': producto.id,
                'nombre_producto': producto.nombre_producto,
                'marca': producto.marca,
                'categoria': producto.categoria,
                'precio_costo': producto.precio_costo,
                'precio_venta':producto.precio_venta,
                'fecha_venc': producto.fecha_venc

            })

        return Response(productos_datos, status=status.HTTP_200_OK)

    def post(self, request):
        #POST PARA CREAR UN PRODUCTO NUEVO O INGRESARLO AL SISTEMA EXCLUSIVO DE ADMIN 
        nombre_producto = request.data.get('nombre_producto')
        marca = request.data.get('marca')
        categoria = request.data.get('categoria')
        precio_costo = request.data.get('precio_costo')
        precio_venta = request.data.get('precio_venta')
        fecha_venc = request.data.get('fecha_venc')

       
        if not nombre_producto or not marca or not categoria or not precio_costo or not precio_venta or not fecha_venc is None:
            return Response({
                'mensaje': 'Los campos no pueden estar vacios'
            }, status=status.HTTP_400_BAD_REQUEST)

        if precio_costo < 0 or precio_venta <0:
           return Response({
               'error': 'los precios de venta y costo no pueden ser 0 en el registro'
           }, status=status.HTTP_400_BAD_REQUEST)

        if Producto.objects.filter(nombre_producto_iexact=nombre_producto).exists():
            return Response({
                'error': 'El producto no puede tener el mismo nombre'
            }, status=status.HTTP_400_BAD_REQUEST)

        producto = Producto.objects.create(

            nombre_producto = nombre_producto,
            marca = marca,
            categoria = categoria,
            precio_costo = precio_costo,
            precio_venta = precio_venta,
            fecha_venc = fecha_venc if  fecha_venc else None,
        )

        stock_a = request.data.get('stock')
        stock_min_a = request.data.get('stock_min')

        if not stock or not stock_min:
            return Response({
                'error': 'Los campos de stock no pueden estar vacios'
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            stock = int(stock_a)   
            stock_min= int(stock_min_a) 
        except ValueError:
            return Response({
                'error': 'Los campos stock deben ser numericos'
            })
        
        if stock < 0 or stock_min <= 1:
            return Response({
                'error': 'Stock no puede ser menor a cero y stock minimo debe ser mayor o igual a 1 '
            },status=status.HTTP_400_BAD_REQUEST)
       
        Stock.objects.create(
            producto= producto,
            stock = stock,
            stock_min = stock_min,
        )

        return Response({
            'mensaje': 'Producto Creado correctamente',
            'producto': {
                'producto': producto.id,
                'nombre_producto': producto.nombre_producto,
                'marca': producto.marca,
                'categoria': producto.categoria,
                'precio_costo': producto.precio_costo,
                'precio_venta':producto.precio_venta,
                'fecha_venc': producto.fecha_venc 
            }
        },status=status.HTTP_201_CREATED)

#GET PARA CONSULTAR UN PRODUCTO EN ESPECIFICO POR ID ESTA FUNCION SERA EXCLUSIVA PARA ADMIN
class ProductoDetalleApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request, id):
    
        producto = get_object_or_404(Producto, id=id)

        return Response({
                  
            'producto': producto.id,
            'nombre_producto': producto.nombre_producto,
            'marca': producto.marca,
            'categoria': producto.categoria,
            'precio_costo': producto.precio_costo,
            'precio_venta':producto.precio_venta,
            'fecha_venc': producto.fecha_venc 
                    
        },status=status.HTTP_200_OK)

    def put(self,request,id):
    # PUT ES PARA ACTUALIZAR TODOS LOS CAMPOS DE UN PRODUCTO POR MEDIO DE ID ESTE SERA EXCLUSIVA PARA ADMIN
        producto = get_object_or_404(Producto, id=id)

        nombre_producto = request.data.get('nombre_producto')
        marca = request.data.get('marca')
        categoria = request.data.get('categoria')
        precio_costo = request.data.get('precio_costo')
        precio_venta = request.data.get('precio_venta')
        fecha_venc = request.data.get('fecha_venc')

        if not nombre_producto or not marca or not categoria or not precio_costo or not precio_venta or not fecha_venc is None:
            return Response({
                'mensaje': 'Los campos no pueden estar vacios'
            }, status=status.HTTP_400_BAD_REQUEST)

        if precio_costo < 0 or precio_venta < 0:
           return Response({
               'error': 'los precios de venta y costo no pueden ser 0 en el registro'
           }, status=status.HTTP_400_BAD_REQUEST)

        if Producto.objects.filter(nombre_producto_iexact=nombre_producto).exists():
            return Response({
                'error': 'El producto no puede tener el mismo nombre'
            }, status=status.HTTP_400_BAD_REQUEST)

        producto.nombre_producto = nombre_producto
        producto.marca = marca
        producto.categoria = categoria
        producto.precio_costo = precio_costo
        producto.precio_venta = precio_venta
        producto.fecha_venc = fecha_venc 
        producto.save()

        return Response({
            'mensaje': 'Producto de mascotas actualizado',
            'producto': producto.id,
            'nombre_producto': producto.nombre_producto,
            'marca': producto.marca,
            'categoria': producto.categoria,
            'precio_costo': producto.precio_costo,
            'precio_venta':producto.precio_venta,
            'fecha_venc': producto.fecha_venc 
            
        },status=status.HTTP_200_OK)

    def delete(self,request,id):
    # DELETE ES PARA ELIMINAR PRODUCTOS POR ID ES EXCLUSIVA PARA ADMIN
        producto = get_object_or_404(Producto, id=id)

        producto.delete()

        return Response({
            'mensaje': 'Producto Eliminado'}, status=status.HTTP_200_OK)

#APIS CLIENTE PARA ADMIN

class ClienteApiView(APIView):# implementar para registro /  hablar con tobal
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # GET: FUNCION PARA VER A TODOS LOS CLIENTES REGISTRADOS EN EL SISTEMA O QUE SE ENCUENTREN RELACIONADOS 
    # A UNA VENTA O COMPRA, FUNCION EXCLUSIVA DE ADMIN 
    def get(self,request):

        clientes = Cliente.objects.all().order_by('rut')

        clientes_datos = []

        for cliente in clientes:
            clientes_datos.append({
       
            'rut': cliente.rut, #Despues de rut ingresar contraseña he ingresar contra en models asi crear pasa a ser registro
            'nombre': cliente.nombre,
            'correo':cliente.correo,
            'telefono': cliente.telefono,
            'direccion': cliente.direccion   

            })

        return Response(clientes_datos, status=status.HTTP_200_OK)


class ClienteDetalleApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # GET: FUNCION PARA BUSCAR UN CLIENTE EN ESPECIFICO POR MEDIO DE LA ID 

    def get(self, request, id):

        cliente = get_object_or_404(Producto, id=id)

        return Response({
            'cliente': cliente.id,
            'rut': cliente.rut,#La contraseña no deberia de verla el administrador por temas o conceptos de seguridad investigar como resguardar ese dato
            'nombre': cliente.nombre,
            'correo':cliente.correo,
            'telefono': cliente.telefono,
            'direccion': cliente.direccion   

        }, status=status.HTTP_200_OK)

#APIS STOCK PARA ADMIN 

class StockApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    

    # GET: FUNCION PARA LISTAR TODOS LOS PRODUCTOS EN EL STOCK, 
    # FUNCION EXCLUSIVA DE ADMIN

    def get(self,request):

        stocks = Stock.objects.all().order_by('-producto_id')

        stock_datos = []

        for stock in stocks:

            stock_datos.append({
                'id':stock.id,
                'producto': stock.producto_id,
                'stock':stock.stock,
                'stock_min': stock.stock_min

            })
        return Response(stock_datos, status=status.HTTP_200_OK)


class StockDetalleApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # PUT: FUNCION PARA ACTUALIZAR O REPONER CANTIDADES DE LOS PRODUCTOS, 
    # FUNCION EXCLUSIVA DE ADMIN

    def put(self, request, id):

        stock1 = get_object_or_404(Stock, id=id)

        stock_a = request.data.get('stock')
        stock_min_a = request.data.get('stock_min')


        if stock is None or stock_min is None:
                return Response({
                    'error': 'Los campos de stock no pueden estar vacios'
                }, status=status.HTTP_400_BAD_REQUEST)
        try:
            stock = int(stock_a)   
            stock_min= int(stock_min_a) 
        except ValueError:
            return Response({
                'error': 'Los campos stock deben ser numericos'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if stock < 0 or stock_min < 1:
            return Response({
                'error': 'Stock no puede ser menor a cero y stock minimo debe ser mayor o igual a 1 '
            },status=status.HTTP_400_BAD_REQUEST)

        stock1.stock = stock
        stock1.stock_min = stock_min

        stock1.save()

        return Response({

            'id': stock1.id,
            'producto': stock1.producto_id,
            'stock': stock1.stock,
            'stock_min': stock1.stock_min

        }, status=status.HTTP_200_OK)

#APIS DE VENTA PARA ADMIN 

class VentaApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # GET: FUNCION PARA VER LAS VENTAS GENERALES DE LOS PRODUCTOS, 
    # FUNCION EXCLUSIVA DE ADMIN 
    def get(self, request):

        ventas = Venta.objects.all().order_by('-fecha')

        ventas_datos = []

        for venta in ventas:

            ventas_datos.append({

                'id':venta.id,
                'fecha':venta.fecha,
                'cliente':venta.cliente_id,#analizar bien 
                'total':venta.total,
                'metodo_pago':venta.metodo_pago

            })

        return Response(ventas_datos, status=status.HTTP_200_OK)




class DetalleVentaApiView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # GET: FUNCION PARA VER TODOS LOS DETALLES DE VENTAS DE LOS CLIENTES, 
    # FUNCION EXCLUSIVA DE ADMIN

    def get(self, request, id):
        detalles = DetalleVenta.objects.filter(venta_id=id)

        if not detalles.exists():
            return Response({
                'error': 'No se han encontrado detalles para el ID de esta venta'
            }, status=status.HTTP_404_NOT_FOUND)

        detalles_datos = []

        for detalle in detalles:
            detalles_datos.append ({

                'id':detalle.id,
                'venta_id': detalle.venta_id,
                'producto_id': detalle.producto_id,
                'producto_nombre':detalle.producto.nombre_producto,
                'precio_unitario':detalle.precio_unitario,
                'cantidad': detalle.cantidad

            })

        return Response(detalles_datos, status=status.HTTP_200_OK)



# FUNCIONES GENERALES DE CLIENTE CON APIS 


# Funcion de registro para cliente 
#class ResgistroApiView(APIView):
    #permission_classes = [AllowAny]

    def post(self, request):

        rut = request.data.get('rut')
        nombre = request.data.get('nombre')
        correo = request.data.get('correo')
        telefono = request.data.get('telefono')
        direccion = request.data.get('direccion')

        if not rut or not nombre or not correo or not telefono or not direccion:
            return Response({
                'error': 'Los campos de cliente no pueden estar vacios'
            }, status=status.HTTP_400_BAD_REQUEST)

        if Cliente.objects.filter(rut_iexact=rut).exists():
            return Response({
                'error': 'Ese rut ya existe'
            },status=status.HTTP_400_BAD_REQUEST)

        #Crear contraseña 

        cliente = Cliente.objects.create(
            rut = rut,
            nombre = nombre,
            correo = correo,
            telefono = telefono,
            direccion= direccion,
            
        )

        return Response({
    
            'rut': cliente.rut, #Despues de rut ingresar contraseña he ingresar contra en models asi crear pasa a ser registro hacer otro login para usuario o construir una api adicional para registro y aplicar ahi el post de crear usuario 
            'nombre': cliente.nombre,
            'telefono': cliente.telefono,
            'direccion': cliente.direccion   
    
            }, status=status.HTTP_200_OK)
