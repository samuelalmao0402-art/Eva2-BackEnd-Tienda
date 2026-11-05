#Importacion de frameworws de seguridad para django e implmentacion de APIs e implementacion del metodo GET,POST,PUT,DELETE
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.authentication import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import datetime
# Importacion de funciones en models 
from .models import Cliente
from .models import Producto
from .models import Venta
from .models import DetalleVenta
from .models import Stock
from .models import Usuario
from .models import CarritoCompra, ItemCarrito


def login_view(request):
    return render(request, 'tienda_mascotasapp/login.html')

def inicio(request):
    return render(request, 'tienda_mascotasapp/inicio.html')

#Logica de Producto
def ingresar_producto(request):
    return render(request, 'tienda_mascotasapp/ingresar_prod.html')
        
def ver_producto(request):
    return render(request, 'tienda_mascotasapp/ver_prod.html')


def actualizar_producto(request, id):
    # Ahora la función acepta el 'id' que le envía la URL
    return render(request, 'tienda_mascotasapp/editar_prod.html')

def catalogo_view(request):
    return render(request, 'tienda_mascotasapp/catalogo.html')

def catalogo_detalle_view(request, id):
    return render(request, 'tienda_mascotasapp/catalogo_detalle.html', {'producto_id': id})

def carrito_view(request):
    return render(request, 'tienda_mascotasapp/carrito.html')

def checkout_view(request):
    return render(request, 'tienda_mascotasapp/checkout.html')

def compra_exitosa_view(request, id):
    return render(request, 'tienda_mascotasapp/compra_exitosa.html', {'venta_id': id})

def mis_compras_view(request):
    return render(request, 'tienda_mascotasapp/mis_compras.html')

# --- Vista de Detalle de Compra (Cliente) ---
def detalle_compra_view(request, id):
    return render(request, 'tienda_mascotasapp/detalle_compra.html', {'venta_id': id})

def ingresar_cliente(request):
    return render(request, 'tienda_mascotasapp/ingresar_cli.html')

def ver_cliente(request):
    return render(request, 'tienda_mascotasapp/ver_cli.html')

# Logica de Stock
def ver_stock(request):
    return render(request, 'tienda_mascotasapp/lstock.html')

def actualizar_stock(request, id):
    return render(request, 'tienda_mascotasapp/actualizar_stock.html')

def ver_ventas(request):
    return render(request, 'tienda_mascotasapp/ver_ventas.html')

def ver_detalle_venta(request, id):
    return render(request, 'tienda_mascotasapp/ver_detalle_venta.html', {'venta_id': id})

#LOGICA DE NEGOCIO Y APIS APLICADAS

#APIS LOGIN --> REUTILIZAR LA DEL PROFE
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({
                'error': 'Debe ingresar el correo y la contraseña.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 1. Buscamos al usuario directamente en tu tabla personalizada (por username o email)
        usuario = Usuario.objects.filter(username=email).first()
        if not usuario:
            usuario = Usuario.objects.filter(email=email).first()

        # 2. Verificamos que el usuario exista y que la contraseña encriptada coincida
        if not usuario or not usuario.check_password(password):
            return Response({
                'error': 'Credenciales inválidas. Verifique su correo y contraseña.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # 3. Verificar si el usuario está activo
        if not usuario.is_active:
            return Response({
                'error': 'Esta cuenta se encuentra desactivada.'
            }, status=status.HTTP_403_FORBIDDEN)

        # 4. Obtener o crear el Token de acceso para la API REST
        token, created = Token.objects.get_or_create(user=usuario)
        
        # 5. Determinar los privilegios y rol para la respuesta
        es_admin = usuario.is_staff or usuario.is_superuser
        
        # Si es superusuario de Django, forzamos el rol 'admin' para el frontend
        if es_admin:
            rol_usuario = 'admin'
        else:
            # Si es cliente normal, usamos su rol guardado (o 'cliente' por defecto)
            rol_usuario = usuario.roles if hasattr(usuario, 'roles') and usuario.roles else 'cliente'

        return Response({
            'mensaje': '¡Inicio de sesión exitoso!',
            'token': token.key,
            'email': usuario.email if hasattr(usuario, 'email') and usuario.email else usuario.username, 
            'es_admin': es_admin,
            'roles': rol_usuario
        }, status=status.HTTP_200_OK)
    
# API CERRAR SESION
class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # 1. Obtener y eliminar el token asociado a la sesión del usuario
            token = Token.objects.get(user=request.user)
            token.delete()

            return Response({
                'mensaje': 'Sesión cerrada exitosamente.'
            }, status=status.HTTP_200_OK)

        except Token.DoesNotExist:
            return Response({
                'error': 'No se encontró una sesión activa para este usuario.'
            }, status=status.HTTP_400_BAD_REQUEST)

# FUNCIONES GENERALES DE ADIM CON APIS 


#APIS PRODUCTOS PARA ADMIN 

class ProductosApiView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser] # Cambiar por una funcion implementada para que sea administrador por rol
    
    # GET PARA MOSTRAR TODOS LOS PRODUCTOS CON ALL
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
                'fecha_venc': producto.fecha_venc,
                'estado': producto.estado
            })
        return Response(productos_datos, status=status.HTTP_200_OK)

    def post(self, request):
        nombre_producto = request.data.get('nombre_producto')
        marca = request.data.get('marca')
        categoria = request.data.get('categoria')
        precio_costo = request.data.get('precio_costo')
        precio_venta = request.data.get('precio_venta')
        fecha_venc = request.data.get('fecha_venc')
        estado = request.data.get('estado')

        # 1. Validar campos obligatorios de texto y estado
        if not nombre_producto or not marca or not categoria or estado is None:
            return Response({
                'error': 'Los campos obligatorios no pueden estar vacíos.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2. Convertir y validar precios
        try:
            precio_costo = float(precio_costo)
            precio_venta = float(precio_venta)
        except (ValueError, TypeError):
            return Response({
                'error': 'Los precios deben ser valores numéricos válidos.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if precio_costo <= 0 or precio_venta <= 0:
            return Response({
                'error': 'Los precios de costo y venta deben ser mayores a cero.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if Producto.objects.filter(nombre_producto__iexact=nombre_producto).exists():
            return Response({
                'error': 'Ya existe un producto registrado con ese mismo nombre.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3. NUEVA VALIDACIÓN: Control de Fechas de Vencimiento
        if fecha_venc:
            try:
                # Convertimos el texto (ej: "2026-11-22") a un objeto de fecha
                fecha_obj = datetime.strptime(fecha_venc, '%Y-%m-%d').date()
                año_actual = datetime.now().year

                # Bloqueamos años del pasado
                if fecha_obj.year < año_actual:
                    return Response({
                        'error': 'La fecha de vencimiento no puede ser de un año pasado.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Bloqueamos años exagerados (ajusta el 2100 según el límite que consideres lógico)
                if fecha_obj.year > 2100:
                    return Response({
                        'error': 'El año ingresado es demasiado lejano. Por favor, ingresa una fecha adecuada para nuestro siglo.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            except ValueError:
                return Response({
                    'error': 'Formato de fecha inválido. Utiliza el formato correcto.'
                }, status=status.HTTP_400_BAD_REQUEST)

        # 4. Convertir y validar stock
        stock_a = request.data.get('stock')
        stock_min_a = request.data.get('stock_min')

        try:
            stock = int(stock_a)   
            stock_min = int(stock_min_a) 
        except (ValueError, TypeError):
            return Response({
                'error': 'Los campos de stock deben ser números enteros.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if stock < 0 or stock_min < 1:
            return Response({
                'error': 'El stock no puede ser negativo y el stock mínimo debe ser al menos 1.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 5. Crear el Producto
        producto = Producto.objects.create(
            nombre_producto=nombre_producto,
            marca=marca,
            categoria=categoria,
            precio_costo=precio_costo,
            precio_venta=precio_venta,
            fecha_venc=fecha_venc if fecha_venc else None,
            estado=bool(estado)
        )

        # 6. Crear el registro en Stock
        Stock.objects.create(
            producto=producto,
            stock=stock,
            stock_min=stock_min,
        )

        return Response({
            'mensaje': 'Producto y stock creados correctamente.',
            'producto_id': producto.id
        }, status=status.HTTP_201_CREATED)

#GET PARA CONSULTAR UN PRODUCTO EN ESPECIFICO POR ID ESTA FUNCION SERA EXCLUSIVA PARA ADMIN
class ProductoDetalleApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]# Cambiar por una funcion implementada para que sea administrador por rol

    def get(self,request, id):
    
        producto = get_object_or_404(Producto, id=id)

        return Response({ 
            'producto': producto.id,
            'nombre_producto': producto.nombre_producto,
            'marca': producto.marca,
            'categoria': producto.categoria,
            'precio_costo': producto.precio_costo,
            'precio_venta':producto.precio_venta,
            'fecha_venc': producto.fecha_venc,
            'estado': producto.estado
                    
        },status=status.HTTP_200_OK)

    def put(self, request, id):
        # PUT ES PARA ACTUALIZAR TODOS LOS CAMPOS DE UN PRODUCTO POR MEDIO DE ID ESTE SERA EXCLUSIVA PARA ADMIN
        producto = get_object_or_404(Producto, id=id)

        nombre_producto = request.data.get('nombre_producto')
        marca = request.data.get('marca')
        categoria = request.data.get('categoria')
        precio_costo = request.data.get('precio_costo')
        precio_venta = request.data.get('precio_venta')
        fecha_venc = request.data.get('fecha_venc')
        estado = request.data.get('estado')

        # 1. Manejo de fecha vacía: Si desde el HTML llega vacío "", lo pasamos a None para evitar errores en BD
        if fecha_venc == "":
            fecha_venc = None

        if not nombre_producto or not marca or not categoria or precio_costo is None or precio_venta is None or estado is None:
            return Response({
                'mensaje': 'Los campos no pueden estar vacios'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2. SOLUCIÓN AL ERROR: Convertimos los textos a números (float) antes de compararlos
        try:
            precio_costo = float(precio_costo)
            precio_venta = float(precio_venta)
        except (ValueError, TypeError):
            return Response({
                'error': 'Los precios deben ser valores numéricos válidos'
            }, status=status.HTTP_400_BAD_REQUEST)

        if precio_costo < 0 or precio_venta < 0:
            return Response({
                'error': 'los precios de venta y costo no pueden ser menores a 0 en el registro'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3. NUEVA VALIDACIÓN: Control de Fechas de Vencimiento para la actualización
        if fecha_venc:
            try:
                fecha_obj = datetime.strptime(fecha_venc, '%Y-%m-%d').date()
                año_actual = datetime.now().year

                if fecha_obj.year < año_actual:
                    return Response({
                        'error': 'La fecha de vencimiento no puede ser de un año pasado.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if fecha_obj.year > 2100:
                    return Response({
                        'error': 'El año ingresado es demasiado lejano. Por favor, ingresa una fecha adecuada para nuestro siglo.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            except ValueError:
                return Response({
                    'error': 'Formato de fecha inválido. Utiliza el formato correcto.'
                }, status=status.HTTP_400_BAD_REQUEST)

        # 4. SOLUCIÓN DE NOMBRE REPETIDO: Agregamos .exclude(id=id) para que te permita guardar si no cambiaste el nombre
        if Producto.objects.filter(nombre_producto__iexact=nombre_producto).exclude(id=id).exists():
            return Response({
                'error': 'El producto no puede tener el mismo nombre'
            }, status=status.HTTP_400_BAD_REQUEST)

        producto.nombre_producto = nombre_producto
        producto.marca = marca
        producto.categoria = categoria
        producto.precio_costo = precio_costo
        producto.precio_venta = precio_venta
        producto.fecha_venc = fecha_venc 
        
        # 5. Parseo de estado: El HTML envía "true" o "false" como texto, lo pasamos a booleano
        if isinstance(estado, str):
            producto.estado = estado.lower() == 'true'
        else:
            producto.estado = bool(estado)
            
        producto.save()

        return Response({
            'mensaje': 'Producto de mascotas actualizado',
            'producto': producto.id,
            'nombre_producto': producto.nombre_producto,
            'marca': producto.marca,
            'categoria': producto.categoria,
            'precio_costo': producto.precio_costo,
            'precio_venta': producto.precio_venta,
            'fecha_venc': producto.fecha_venc,
            'estado': producto.estado
        }, status=status.HTTP_200_OK)

    def delete(self, request, id):
        # DELETE ES PARA ELIMINAR UN PRODUCTO POR MEDIO DE ID (ADMIN)
        producto = get_object_or_404(Producto, id=id)

        try:
            # Intentamos el borrado físico (funcionará solo si no tiene ventas ni stock asociado)
            producto.delete()
            return Response({
                'mensaje': 'Producto eliminado físicamente de la base de datos'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Si choca por el ProtectedError (ya tiene ventas o stock), aplicamos Soft Delete
            producto.estado = False
            producto.save()
            return Response({
                'mensaje': 'El producto tiene ventas históricas asociadas y no puede ser borrado. Su estado ha sido cambiado a Inactivo.'
            }, status=status.HTTP_200_OK)

#APIS CLIENTE PARA ADMIN

class ClienteApiView(APIView):# implementar para registro /  hablar con tobal
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]# Cambiar por una funcion implementada para que sea administrador 

    # GET: FUNCION PARA VER A TODOS LOS CLIENTES REGISTRADOS EN EL SISTEMA O QUE SE ENCUENTREN RELACIONADOS 
    # A UNA VENTA O COMPRA, FUNCION EXCLUSIVA DE ADMIN 
    def get(self,request):

        clientes = Cliente.objects.all().order_by('rut')

        clientes_datos = []

        for cliente in clientes:
            clientes_datos.append({
            'rut': cliente.rut, #Despues de rut ingresar contraseña he ingresar contra en models asi crear pasa a ser registro
            'nombre': cliente.nombre,
            'email':cliente.usuario.email,
            'telefono': cliente.telefono,
            'direccion': cliente.direccion   

            })

        return Response(clientes_datos, status=status.HTTP_200_OK)


class ClienteDetalleApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]# Cambiar por una funcion implementada para que sea administrador 

    # GET: FUNCION PARA BUSCAR UN CLIENTE EN ESPECIFICO POR MEDIO DE LA ID 

    def get(self, request, id):

        cliente = get_object_or_404(Cliente, id=id)

        return Response({
            'cliente': cliente.id,
            'rut': cliente.rut,#La contraseña no deberia de verla el administrador por temas o conceptos de seguridad investigar como resguardar ese dato
            'nombre': cliente.nombre,
            'email':cliente.usuario.email,
            'telefono': cliente.telefono,
            'direccion': cliente.direccion   

        }, status=status.HTTP_200_OK)

#APIS STOCK PARA ADMIN 

class StockApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser] 

    def get(self,request):
        stocks = Stock.objects.all().order_by('-producto_id')
        stock_datos = []

        for stock in stocks:
            stock_datos.append({
                'id': stock.id,
                'producto': stock.producto_id,
                # Extraemos el nombre del producto desde la relación para mostrarlo en la tabla
                'nombre_producto': stock.producto.nombre_producto, 
                'stock': stock.stock,
                'stock_min': stock.stock_min
            })
        return Response(stock_datos, status=status.HTTP_200_OK)

class StockDetalleApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, id):
        stock1 = get_object_or_404(Stock, id=id)
        return Response({
            'id': stock1.id,
            'producto': stock1.producto_id,
            'nombre_producto': stock1.producto.nombre_producto,
            'stock': stock1.stock,
            'stock_min': stock1.stock_min
        }, status=status.HTTP_200_OK)

    def put(self, request, id):
        stock1 = get_object_or_404(Stock, id=id)

        stock_a = request.data.get('stock')
        stock_min_a = request.data.get('stock_min')

        if stock_a is None or stock_min_a is None:
                return Response({
                    'error': 'Los campos de stock no pueden estar vacíos'
                }, status=status.HTTP_400_BAD_REQUEST)
        try:
            stock_val = int(stock_a)   
            stock_min_val = int(stock_min_a) 
        except ValueError:
            return Response({
                'error': 'Los campos stock deben ser numéricos'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if stock_val < 0 or stock_min_val < 1:
            return Response({
                'error': 'Stock no puede ser menor a cero y stock mínimo debe ser 1 o más'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 1. Guardamos en la tabla Stock
        stock1.stock = stock_val
        stock1.stock_min = stock_min_val
        stock1.save()

        # 2. EL TRUCO: Sincronizamos también la tabla Producto para que la pantalla principal se actualice
        try:
            producto_relacionado = stock1.producto
            # Actualizamos ambos posibles nombres de campo por seguridad
            if hasattr(producto_relacionado, 'stock_disponible'):
                producto_relacionado.stock_disponible = stock_val
            if hasattr(producto_relacionado, 'stock'):
                producto_relacionado.stock = stock_val
            producto_relacionado.save()
        except Exception:
            pass # Si choca, lo ignora y sigue sin romper la página

        return Response({
            'id': stock1.id,
            'producto': stock1.producto_id,
            'stock': stock1.stock,
            'stock_min': stock1.stock_min
        }, status=status.HTTP_200_OK)

#APIS DE VENTA PARA ADMIN 

class VentaApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):

        ventas = Venta.objects.all().order_by('-fecha')

        ventas_datos = []

        for venta in ventas:
            nombre_real = venta.cliente.nombre if venta.cliente else "Desconocido"
            rut_real = venta.cliente.rut if venta.cliente else "Sin RUT"

            ventas_datos.append({
                'id': venta.id,
                'fecha': venta.fecha,
                'cliente': nombre_real,       
                'cliente_rut': rut_real,      
                'total': venta.total,
                'metodo_pago': venta.metodo_pago
            })

        return Response(ventas_datos, status=status.HTTP_200_OK)




class DetalleVentaApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, id):
        # 1. Buscamos la venta específica
        venta = get_object_or_404(Venta, id=id)

        # 2. Extraemos los datos del cliente
        nombre_real = venta.cliente.nombre if venta.cliente else "Desconocido"
        rut_real = venta.cliente.rut if venta.cliente else "Sin RUT"

        # 3. Buscamos todos los productos asociados a esta boleta
        detalles = DetalleVenta.objects.filter(venta=venta)
        detalles_datos = []

        for item in detalles:
            detalles_datos.append({
                'producto_nombre': item.producto.nombre_producto if item.producto else "Producto eliminado",
                'precio_unitario': getattr(item, 'precio', getattr(item, 'precio_unitario', 0)),
                
                # LA SOLUCIÓN: Busca 'cantidad' y si no existe, busca 'cantidad_producto' para no chocar
                'cantidad': getattr(item, 'cantidad', getattr(item, 'cantidad_producto', 0)),
                
                'subtotal': getattr(item, 'subtotal', 0)
            })

        # 4. Enviamos el paquete completo
        return Response({
            'fecha': venta.fecha,
            'cliente_nombre': nombre_real,
            'cliente_rut': rut_real,
            'metodo_pago': venta.metodo_pago,
            'total': venta.total,
            'detalles': detalles_datos
        }, status=status.HTTP_200_OK)



# FUNCIONES GENERALES DE CLIENTE CON APIS 


# Funcion de registro para cliente 
class RegistroApiView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):

        email = request.data.get('email')
        password_plana = request.data.get('password')
        rut = request.data.get('rut')
        nombre = request.data.get('nombre')
        telefono = request.data.get('telefono')
        direccion = request.data.get('direccion')

        if not email or not password_plana or not rut or not nombre or not telefono or not direccion:
            return Response({
                'error': 'Los campos de cliente no pueden estar vacios, rellenalos'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # NUEVA VALIDACIÓN: Comprobamos que el RUT tenga entre 9 y 10 caracteres
        if len(rut) < 9 or len(rut) > 10:
            return Response({
                'error': 'El RUT ingresado no es válido. Debe tener entre 9 y 10 caracteres (incluyendo el guion).'
            }, status=status.HTTP_400_BAD_REQUEST)

        # CON UN LEN RECORREMOS EL ESCRITO Y COMPROBAMOS QUE LA CANTIDAD DE CARACTERES NO SEA MENOR A 10
        if len(password_plana) < 10:
            return Response({
                'error': 'La contraseña debe conetener al menos 10 caracteres'
            },status=status.HTTP_400_BAD_REQUEST)

        # CON EL TRY Y EXCEPT VALIDAMOS QUE EL USUARIO NO INGRESE CONTRASEÑAS POCO SEGURAS ADEMAS DE 
        try:
            validate_password(password_plana)

        except Exception:
            return Response({
                'error': 'La contraseña es muy corta o su combinacion es insegura'
            }, status=status.HTTP_400_BAD_REQUEST)

        if Cliente.objects.filter(rut__iexact=rut).exists():
            return Response({
                'error': 'Ese rut ya existe en el sistema'
            },status=status.HTTP_400_BAD_REQUEST)
        
        if Usuario.objects.filter(email__iexact=email).exists():
            return Response({
                'error': 'Ese correo ya se encuentra registrado'
            },status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():  
        # VALIDAMOS LA CONTRASEÑA CON LA CONFIGURACION DE MAKE_PASSWORD UNA FUNCION QUE PROTEJE LAS CONTRASEÑAS EN SHA256 Y PBKDF2 Y NO SE ALMACENARA EN TEXTO PLANO
                usuario = Usuario.objects.create_user(
                    username=email,
                    email=email,
                    password=password_plana,
                    roles='cliente'
                )

                cliente = Cliente.objects.create(
                    usuario = usuario,
                    rut = rut,
                    nombre = nombre,
                    telefono = telefono,
                    direccion= direccion,
                    
                )
            return Response({
                'mensaje': 'Cliente registrado exitosamente',
                'rut': cliente.rut, 
                'nombre': cliente.nombre,
                'email': cliente.usuario.email,
                'telefono': cliente.telefono,
                'direccion': cliente.direccion
                # a password--> por temas de seguridad se excluye para no mostrar la contraseña ni de manera hasheada
        
                }, status=status.HTTP_201_CREATED)
        
        except Exception:
            return Response(
                {'error': 'Ocurrió un error inesperado al registrar el cliente.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 1. CatalogoProductoApiView --> productos de manera general
class CatalogoProductoApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        nombre_producto = request.query_params.get('nombre_producto', None)
        categoria = request.query_params.get('categoria', None)

        # Filtramos productos activos con stock mayor a 0
        productos = Producto.objects.filter(estado=True, stock__stock__gt=0).distinct()

        if nombre_producto:
            productos = productos.filter(nombre_producto__icontains=nombre_producto)
        if categoria:
            productos = productos.filter(categoria__icontains=categoria)

        # ARMADO MANUAL DEL JSON (Reemplazo del Serializer)
        data = []
        for p in productos:
            stock_obj = Stock.objects.filter(producto=p).first()
            data.append({
                'id': p.id,
                'nombre_producto': p.nombre_producto,
                'marca': p.marca,
                'categoria': p.categoria,
                'precio_venta': float(p.precio_venta),  # Convertimos Decimal a float para el JSON
                'stock_disponible': stock_obj.stock if stock_obj else 0,
                'estado': p.estado
            })

        return Response(data, status=status.HTTP_200_OK)


# 2. CatalogoDetalleApiView --> buscar un producto especifico
class CatalogoDetalleApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk, estado=True)
        stock_obj = Stock.objects.filter(producto=producto).first()
        
        # Diccionario manual
        data = {
            'id': producto.id,
            'nombre_producto': producto.nombre_producto,
            'marca': producto.marca,
            'categoria': producto.categoria,
            'precio_venta': float(producto.precio_venta),
            'stock_disponible': stock_obj.stock if stock_obj else 0,
            'fecha_venc': str(producto.fecha_venc) if producto.fecha_venc else None,
            'estado': producto.estado
        }
        
        return Response(data, status=status.HTTP_200_OK)


# 3. CarritoApiView --> para ver el carrito de compras
class CarritoApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cliente = get_object_or_404(Cliente, usuario=request.user)
        carrito, _ = CarritoCompra.objects.get_or_create(cliente=cliente)
        
        items = carrito.items.all()
        items_data = []
        total_carrito = 0

        for item in items:
            subtotal = item.producto.precio_venta * item.cantidad_compra
            total_carrito += subtotal
            items_data.append({
                'item_id': item.id,
                'producto_id': item.producto.id,
                'nombre_producto': item.producto.nombre_producto,
                'precio_unitario': float(item.producto.precio_venta),
                'cantidad_compra': item.cantidad_compra,
                'subtotal': float(subtotal)
            })

        data = {
            'carrito_id': carrito.id,
            'cliente': cliente.nombre,
            'items': items_data,
            'total': float(total_carrito)
        }

        return Response(data, status=status.HTTP_200_OK)


# 4. ItemCarritoApiView --> agregar / modificar compras de productos
class ItemCarritoApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # EXTRACCIÓN Y VALIDACIÓN MANUAL (Reemplazo del Serializer)
        producto_id = request.data.get('producto_id')
        cantidad = request.data.get('cantidad_compra', 1)

        if not producto_id:
            return Response({'error': 'Debe enviar el producto_id.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            return Response({'error': 'La cantidad debe ser un número entero mayor a 0.'}, status=status.HTTP_400_BAD_REQUEST)

        producto = get_object_or_404(Producto, id=producto_id, estado=True)
        stock_obj = Stock.objects.filter(producto=producto).first()

        if not stock_obj or stock_obj.stock < cantidad:
            return Response({'error': 'Stock insuficiente.'}, status=status.HTTP_400_BAD_REQUEST)

        cliente = get_object_or_404(Cliente, usuario=request.user)
        carrito, _ = CarritoCompra.objects.get_or_create(cliente=cliente)
        
        item, created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)

        if not created:
            if stock_obj.stock < (item.cantidad_compra + cantidad):
                return Response({'error': 'Stock insuficiente para sumar esa cantidad.'}, status=status.HTTP_400_BAD_REQUEST)
            item.cantidad_compra += cantidad
        else:
            item.cantidad_compra = cantidad

        item.save()

        # Retornamos los datos del item actualizado
        data = {
            'item_id': item.id,
            'producto': producto.nombre_producto,
            'cantidad_compra': item.cantidad_compra,
            'subtotal': float(producto.precio_venta * item.cantidad_compra)
        }
        return Response(data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        cliente = get_object_or_404(Cliente, usuario=request.user)
        item = get_object_or_404(ItemCarrito, pk=pk, carrito__cliente=cliente)
        item.delete()
        return Response({'mensaje': 'Producto eliminado del carrito.'}, status=status.HTTP_204_NO_CONTENT)


# 5. RegistrarCompraApiView --> crea la cabecera de la venta
class RegistrarCompraApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cliente = get_object_or_404(Cliente, usuario=request.user)
        carrito = get_object_or_404(CarritoCompra, cliente=cliente)
        items = carrito.items.all()

        if not items.exists():
            return Response({'error': 'El carrito no tiene productos.'}, status=status.HTTP_400_BAD_REQUEST)

        metodo_pago = request.data.get('metodo_pago', 'Debito')
        entrega = request.data.get('entrega', 'Presencial')

        # Calculamos el total manualmente
        total = sum(item.producto.precio_venta * item.cantidad_compra for item in items)
        
        venta = Venta.objects.create(
            cliente=cliente,
            fecha=timezone.now().date(),
            total=total,
            metodo_pago=metodo_pago,
            entrega=entrega
        )

        return Response({
            'mensaje': 'Orden generada',
            'venta_id': venta.id, 
            'total': float(total)
        }, status=status.HTTP_201_CREATED)


# 6. FinalizarCompraApiView --> Para finalizar, descontar stock y limpiar carrito
class FinalizarCompraApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, venta_id):
        cliente = get_object_or_404(Cliente, usuario=request.user)
        venta = get_object_or_404(Venta, id=venta_id, cliente=cliente)
        carrito = get_object_or_404(CarritoCompra, cliente=cliente)
        
        # Bloqueamos los items para evitar problemas de concurrencia
        items = carrito.items.select_for_update().all()

        if not items.exists():
            return Response({'error': 'El carrito está vacío.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Validar disponibilidad de stock antes de descontar
        for item in items:
            stock_obj = Stock.objects.select_for_update().filter(producto=item.producto).first()
            if not stock_obj or stock_obj.stock < item.cantidad_compra:
                return Response(
                    {'error': f'Stock insuficiente para {item.producto.nombre_producto}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 2. Descontar stock y registrar DetalleVenta
        for item in items:
            stock_obj = Stock.objects.get(producto=item.producto)
            stock_obj.stock -= item.cantidad_compra
            stock_obj.save()

            DetalleVenta.objects.create(
                venta=venta,
                producto=item.producto,
                cantidad_producto=item.cantidad_compra,
                precio_unitario=item.producto.precio_venta
            )

        # 3. Vaciar el carrito tras compra exitosa
        items.delete()

        return Response({'mensaje': 'Compra procesada y stock descontado exitosamente.', 'venta_id': venta.id}, status=status.HTTP_200_OK)


# 7. DetalleCompraApiView --> ver la compra o compras realizadas
class DetalleCompraApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        cliente = get_object_or_404(Cliente, usuario=request.user)
        
        if pk:
            # Traer una venta en específico
            venta = get_object_or_404(Venta, pk=pk, cliente=cliente)
            detalles_venta = DetalleVenta.objects.filter(venta=venta)
            
            lista_detalles = []
            for d in detalles_venta:
                lista_detalles.append({
                    'producto': d.producto.nombre_producto,
                    'cantidad': d.cantidad_producto,
                    'precio_unitario': float(d.precio_unitario),
                    'subtotal': float(d.precio_unitario * d.cantidad_producto)
                })

            data = {
                'id_venta': venta.id,
                'fecha': str(venta.fecha),
                'total': float(venta.total),
                'metodo_pago': venta.metodo_pago,
                'entrega': venta.entrega,
                'detalles': lista_detalles
            }
            return Response(data, status=status.HTTP_200_OK)

        # Traer todas las compras del cliente si no hay PK
        ventas = Venta.objects.filter(cliente=cliente).order_by('-fecha')
        data_ventas = []
        
        for v in ventas:
            data_ventas.append({
                'id_venta': v.id,
                'fecha': str(v.fecha),
                'total': float(v.total),
                'metodo_pago': v.metodo_pago
            })
            
        return Response(data_ventas, status=status.HTTP_200_OK)