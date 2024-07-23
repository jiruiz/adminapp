from traceback import format_tb
from django.db import models
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User


# Create your models here.
class Producto(models.Model):
    nombre = models.CharField(verbose_name="Producto", max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        verbose_name= "Producto"
        verbose_name_plural= "Productos"
        ordering = ["nombre"]#aca le doy el orden a la lista en la web misma , no en el admin
        

    def __str__(self):
        return f"{self.nombre}"
            
            
    # @admin.display(ordering="nombre")
    # def nombrePresentacion(self):
    #     return format_html(self.nombre[:2]+"...")
        

# class Cliente(models.Model):
#     nombre
#     telefono
#     mail
#     domicilio
    
    