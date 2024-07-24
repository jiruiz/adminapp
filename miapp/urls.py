

from django.urls import path, include
from .views import *

urlpatterns = [
   path('',HomreView.as_view(),name="home"),
   path('producto/',ProductoList.as_view(),name="producto"),
   path('cliente/',ClienteList.as_view(),name="cliente"),
   path('turno/',TurnoList.as_view(),name="turno"),
   
   
    path('producto_create/',ProductoCreate.as_view(),name="producto_create"),
]


