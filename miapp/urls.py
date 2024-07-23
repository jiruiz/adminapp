

from django.urls import path, include
from .views import *

urlpatterns = [
   path('',HomreView.as_view(),name="home"),
   path('producto/',ProductoList.as_view(),name="producto"),
]

