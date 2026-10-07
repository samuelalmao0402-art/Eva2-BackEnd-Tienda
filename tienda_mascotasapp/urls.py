from django.urls import path
from . import views

urlpatterns = [
    # Inicio
    path('', views.inicio, name='inicio'),

    # Rutas de Productos
    path('ingresar_producto/', views.ingresar_producto, name='ingresar_producto'),
    path('ver_producto/<int:id>/', views.ver_producto, name='ver_producto'),
    path('eliminar_producto/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('actualizar_producto/<int:id>/', views.actualizar_producto, name='actualizar_producto'),

    # Rutas de Clientes
    path('ingresar_cliente/', views.ingresar_cliente, name='ingresar_cliente'),
    path('ver_cliente/<int:id>/', views.ver_cliente, name='ver_cliente'),

    # Rutas de Stock
    path('ver_stock/', views.ver_stock, name='ver_stock'),
    path('actualizar_stock/<int:id>/', views.actualizar_stock, name='actualizar_stock'),

    # Rutas de Ventas
    path('registrar_venta/', views.registrar_venta, name='registrar_venta'),
    path('ver_ventas/', views.ver_ventas, name='ver_ventas'),
    path('ver_detalle_venta/<int:id>/', views.ver_detalle_venta, name='ver_detalle_venta'),
]