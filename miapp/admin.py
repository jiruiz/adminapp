from django.contrib import admin
from .models import Producto, Cliente, Turno, ProductoSeleccionado,Carrito

# Define the admin interface for Producto
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'created', 'updated', 'image1', 'image2', 'image3', 'image4')
    list_filter = ('nombre', 'created')
    ordering = ('nombre',)

# Define the admin interface for Cliente
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'domicilio', 'Preferencia')

# Define the admin interface for Turno
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'productos_list', 'fecha_hora', 'duracion', 'created', 'updated')
    filter_horizontal = ('productos',)

    def productos_list(self, obj):
        return ", ".join([p.nombre for p in obj.productos.all()])
    productos_list.short_description = 'Productos'

# Define the admin interface for ProductoSeleccionado
class ProductoSeleccionadoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'user', 'cantidad', 'fecha_seleccion')
    list_filter = ('user', 'producto', 'fecha_seleccion')
    ordering = ('-fecha_seleccion',)


# Configuración del admin para el modelo Carrito
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'cantidad', 'fecha_agregado')
    search_fields = ('usuario__username', 'producto__nombre')
    list_filter = ('usuario', 'producto')
    ordering = ('-fecha_agregado',)



# Register the models with the admin interface
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Turno, TurnoAdmin)
admin.site.register(ProductoSeleccionado, ProductoSeleccionadoAdmin)
admin.site.register(Carrito, CarritoAdmin)
