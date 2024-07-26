from django.shortcuts import render

from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView

from .models import *
from .forms import *

# Create your views here.


class HomreView(TemplateView):
    template_name = "miapp/home.html"



# [------------------------ SE CREAN LAS LISTAS PARA VER LOS MODELOS (LISTADOS DE REGISTROS)--------------------------------]    
class ProductoList(ListView):    
    model = Producto
    
    def get_queryset(self):
        return Producto.objects.all().order_by('id').values()
        #return Producto.objects.filter(nombre__icontains='a').values()
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Listado Productos"
        return contexto

    
class ClienteList(ListView):
    model = Cliente
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Listado Clientes"
        # Ejemplo de como podemos traer al  contexto de del html todos los productos
        # contexto['productos'] = Producto.objects.all().values()
        return contexto
    
    
class TurnoList(ListView):
    model = Turno   
    template_name = 'miapp/turno_list.html'  # Asegúrate de que el nombre del archivo sea correcto
    context_object_name = 'object_list' 
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Listado Turnos"
        return contexto
    

# [------------------------ SE CREAN LAS LISTAS PARA INGRESAR LOS MODELOS (ALTA DE REGISTROS)---------------------------------------]   
class ProductoCreate(CreateView):
       model = Producto
       form_class = ProductoForm
       success_url = reverse_lazy('producto')# Redirigimos cuando se registra

class ClienteCreate(CreateView):
       model = Cliente
       form_class = ClienteForm
       success_url = reverse_lazy('cliente')



# [------------------------ SE CREAN LAS LISTAS PARA ACTUALIZAR LOS MODELOS (MODIFICACIÓN DE REGISTROS)-----------------------------]       
class ProductoUpdate(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name_suffix = "_update_form"      
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Modificar Producto" # Establecemos el titulo del html
        return contexto
    def get_success_url(self):
        return reverse_lazy('producto_update',args=[self.object.id])+'?ok'


class ClienteUpdate(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name_suffix = "_update_form"      
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Modificar Cliente" # Establecemos el titulo del html
        return contexto
    def get_success_url(self):
        return reverse_lazy('cliente_update',args=[self.object.id])+'?ok'

    
# [------------------------ SE CREAN LAS LISTAS PARA ELIMINAR LOS MODELOS (ELIMINACIÓN DE REGISTROS)--------------------------------]   
class ProductoDelete(DeleteView):
    model = Producto
    success_url = reverse_lazy('producto')    
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Eliminar Producto"
        return contexto
    
class ClienteDelete(DeleteView):
    model = Cliente
    success_url = reverse_lazy('cliente')    
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Eliminar Cliente"
        return contexto    
    
    
    