from django.shortcuts import render

from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView

from .models import *
from .forms import *

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
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Clientes"
        # Ejemplo de como podemos traer al  contexto de del html todos los productos
        # contexto['productos'] = Producto.objects.all().values()
        return contexto
    
    
class TurnoList(ListView):
    model = Turno   
    template_name = 'miapp/turno_list.html'  # Asegúrate de que el nombre del archivo sea correcto

    context_object_name = 'object_list' 
    
    
class ProductoCreate(CreateView):
       model = Producto
       form_class = ProductoForm
       success_url = reverse_lazy('producto')
       
class ProductoUpdate(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name_suffix = "_update_form"      
    
    def get_success_url(self):
        return reverse_lazy('producto_update',args=[self.object.id])+'?ok'
    
    
class ProductoDelete(DeleteView):
    model = Producto
    success_url = reverse_lazy('producto')    
    