

from django.urls import path, include
from .views import *

urlpatterns = [
   path('',HomreView.as_view(),name="home"),
   path('producto/',ProductoList.as_view(),name="producto"),
   path('cliente/',ClienteList.as_view(),name="cliente"),
   path('turno/',TurnoList.as_view(),name="turno"),
   
    # AMB productos
    path('producto_create/',ProductoCreate.as_view(),name="producto_create"),
    path('producto_update/<int:pk>/', ProductoUpdate.as_view(), name="producto_update"),
    path('producto_delete/<int:pk>/',  ProductoDelete.as_view(), name="producto_delete"),
    
    # ABM Clientes
    path('cliente_create/',ClienteCreate.as_view(),name="cliente_create"),
]


