from django.shortcuts import render

from django.views.generic import TemplateView
from django.views.generic import ListView

from .models import *

# Create your views here.

class HomreView(TemplateView):
    template_name = "miapp/home.html"
    
class ProductoList(ListView):    
    model = Producto
    
    def get_queryset(self):
        return Producto.objects.all().order_by('id').values()
        #return Producto.objects.filter(nombre__icontains='a').values()


    
class ClienteList(ListView):
    model = Cliente
    