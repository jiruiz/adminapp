from django.contrib import admin
from .models import Producto, Cliente, Turno

# Define the admin interface for Producto
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'created', 'updated','image1','image2','image3','image4',)
    list_filter = ('nombre', 'created',)
    ordering = ('nombre',)

# Define the admin interface for Cliente
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'domicilio', 'Preferencia')

# Define the admin interface for Turno
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'productos_list', 'duracion', 'created', 'updated')
    filter_horizontal = ('productos',)


# Register the models with the admin interface
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Turno, TurnoAdmin)
