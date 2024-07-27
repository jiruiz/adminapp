

from django.urls import path, include
from .views import *

urlpatterns = [
   path('',HomreView.as_view(),name="home"),
   path('home_ventas/',HomeViewVentas.as_view(),name="home_ventas"),
   
   
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


