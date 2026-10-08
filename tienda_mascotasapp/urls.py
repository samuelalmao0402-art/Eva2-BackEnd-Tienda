from django.urls import path
from . import views

urlpatterns = [
    # Inicio
    path('', views.inicio, name='inicio'),

    # Rutas de Productos
    path('ingresar_producto/', views.ingresar_producto, name='ingresar_prod'),
    path('ver_producto/<int:id>/', views.ver_producto, name='ver_prod'),
    path('eliminar_producto/<int:id>/', views.eliminar_producto, name='eliminar_prod'),
    path('actualizar_producto/<int:id>/', views.actualizar_producto, name='editar_prod'),

    # Rutas de Clientes
    path('ingresar_cliente/', views.ingresar_cliente, name='ingresar_cli'),
    path('ver_cliente/<int:id>/', views.ver_cliente, name='ver_cli'),

    # Rutas de Stock
    path('ver_stock/', views.ver_stock, name='lstock'),
    path('actualizar_stock/<int:id>/', views.actualizar_stock, name='actualizar_stock'),

    # Rutas de Ventas
    path('registrar_venta/', views.registrar_venta, name='registrar_venta'),
    path('ver_ventas/', views.ver_ventas, name='ver_ventas'),
    path('ver_detalle_venta/<int:id>/', views.ver_detalle_venta, name='ver_detalle_venta'),
]