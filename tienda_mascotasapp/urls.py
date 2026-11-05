from django.urls import path
from . import views

urlpatterns = [
    # --- LA RAÍZ Y EL LOGIN APUNTAN A LA VISTA CORRECTA ---
    path('', views.login_view, name='raiz'),
    path('login/', views.login_view, name='login'),

    # --- PANEL DE ADMINISTRACIÓN (Accesible tras iniciar sesión) ---
    path('inicio/', views.inicio, name='inicio'),

    # Rutas de Productos (Admin)
    path('ingresar_producto/', views.ingresar_producto, name='ingresar_prod'),
    path('ver_productos/', views.ver_producto, name='ver_prod'), 
    path('actualizar_producto/<int:id>/', views.actualizar_producto, name='editar_prod'),

    # Rutas de Clientes (Admin)
    path('ingresar_cliente/', views.ingresar_cliente, name='ingresar_cli'),
    path('ver_clientes/', views.ver_cliente, name='ver_clientes'), 

    # Rutas de Stock (Admin)
    path('ver_stock/', views.ver_stock, name='lstock'),
    path('actualizar_stock/<int:id>/', views.actualizar_stock, name='actualizar_stock'),

    # Rutas de Ventas (Admin)
    path('ver_ventas/', views.ver_ventas, name='ver_ventas'),
    path('ver_detalle_venta/<int:id>/', views.ver_detalle_venta, name='ver_detalle_venta'),

    # --- RUTAS DE VISTAS (RENDER HTML PARA EL CLIENTE) ---
    path('catalogo/', views.catalogo_view, name='catalogo'),
    path('catalogo/<int:id>/', views.catalogo_detalle_view, name='catalogo_detalle'),
    path('carrito/', views.carrito_view, name='carrito'),
    path('checkout/', views.checkout_view, name='checkout'),
    
    # ¡Corregido: Ahora recibe el ID de la venta!
    path('compra_exitosa/<int:id>/', views.compra_exitosa_view, name='compra_exitosa'), 
    
    path('compras/', views.mis_compras_view, name='mis_compras'),
    path('compra/<int:id>/', views.detalle_compra_view, name='detalle_compra'),

    # --- APIs REST (ADMIN Y GENERAL) ---
    path('api/login/', views.LoginAPIView.as_view(), name='login_api'),
    path('api/logout/', views.LogoutAPIView.as_view(), name='logout_api'),
    
    path('api/cliente/', views.ClienteApiView.as_view(), name='api_cliente'),
    path('api/cliente/<int:id>/', views.ClienteDetalleApiView.as_view(), name='api_cliente_detalle'),
    
    path('api/stock/', views.StockApiView.as_view(), name='api_stock'),
    path('api/stock/<int:id>/', views.StockDetalleApiView.as_view(), name='api_stock_actualizar'),
    
    path('api/venta/', views.VentaApiView.as_view(), name='api_venta'),
    path('api/venta/<int:id>/', views.DetalleVentaApiView.as_view(), name='api_venta_detalle'),

    path('api/producto/', views.ProductosApiView.as_view(), name='api_producto'),
    path('api/producto/<int:id>/', views.ProductoDetalleApiView.as_view(), name='api_producto_detalle'),

    # --- APIs REST (CLIENTE FUNCIONALIDADES) ---
    path('api/registro/', views.RegistroApiView.as_view(), name='api_registro_cliente'),
    
    path('api/catalogo/', views.CatalogoProductoApiView.as_view(), name='api_catalogo'),
    path('api/catalogo/<int:pk>/', views.CatalogoDetalleApiView.as_view(), name='api_catalogo_detalle'),
    
    path('api/carrito/', views.CarritoApiView.as_view(), name='api_carrito'),
    path('api/carrito/items/', views.ItemCarritoApiView.as_view(), name='api_carrito_items'),
    path('api/carrito/items/<int:pk>/', views.ItemCarritoApiView.as_view(), name='api_itemcarrito_detalle'),
    
    path('api/registrocompra/', views.RegistrarCompraApiView.as_view(), name='api_registro_compra'),
    
    # --- RUTA NUEVA: LISTA GENERAL DE COMPRAS ---
    path('api/mis_compras/', views.DetalleCompraApiView.as_view(), name='api_mis_compras_lista'),
    
    # --- RUTA EXISTENTE: DETALLE DE UNA SOLA COMPRA ---
    path('api/detallecompra/<int:pk>/', views.DetalleCompraApiView.as_view(), name='api_detalle_compra'),
    
    # ¡Corregido: Ahora se llama venta_id para coincidir con tu views.py!
    path('api/finalizarcompra/<int:venta_id>/', views.FinalizarCompraApiView.as_view(), name='api_finalizar_compra'), 
]