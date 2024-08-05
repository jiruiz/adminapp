

from django.urls import path, include
from .views import *


from django.contrib.auth.views import LogoutView


urlpatterns = [
   path('',HomreView.as_view(),name="home"),
   path('home_ventas/',HomeViewVentas.as_view(),name="home_ventas"),
   path('search_results/', ProductSearchView.as_view(), name='search_results'),
   path('login/', MyLoginView.as_view(), name='login'),
   path('logout/', LogoutView.as_view(next_page='home_ventas'), name='logout'),
   path('confirmar_turno/', ConfirmarTurnoView.as_view(), name='confirmar_turno'),
   path('agregar-al-carrito/', AgregarAlCarritoView.as_view(), name='agregar_al_carrito'),
   path('crear-turno/', CrearTurnoView.as_view(), name='crear_turno'),
   path('eliminar/<int:item_id>/', EliminarDelCarritoView.as_view(), name='eliminar'),
   path('aumentar/<int:item_id>/', AumentarCantidadView.as_view(), name='aumentar'),
   path('disminuir/<int:item_id>/', DisminuirCantidadView.as_view(), name='disminuir'),
   path('agenda/', AgendaView.as_view(), name='agenda'),
   path('no_registrado/', NoRegistradoView.as_view(), name='no_registrado'),
   path('registro/', RegistroUsuario.as_view(), name="registro"),

   
   
   
   
   
   path('producto/',ProductoList.as_view(),name="producto"),
   path('cliente/',ClienteList.as_view(),name="cliente"),
   path('turno/',TurnoList.as_view(),name="turno"),
   
    # AMB productos
    path('producto_create/',ProductoCreate.as_view(),name="producto_create"),
    path('producto_update/<int:pk>/', ProductoUpdate.as_view(), name="producto_update"),
    path('producto_delete/<int:pk>/',  ProductoDelete.as_view(), name="producto_delete"),
    
    # ABM Clientes
    path('cliente_create/',ClienteCreate.as_view(),name="cliente_create"),
    path('cliente_update/<int:pk>/', ClienteUpdate.as_view(), name="cliente_update"),
    path('cliente_delete/<int:pk>/',  ClienteDelete.as_view(), name="cliente_delete"),

    # ABM Clientes
    path('turno_create/',TurnoCreate.as_view(),name="turno_create"),
    path('turno_update/<int:pk>/', TurnoUpdate.as_view(), name="turno_update"),
    path('turno_delete/<int:pk>/',  TurnoDelete.as_view(), name="turno_delete"),

]


