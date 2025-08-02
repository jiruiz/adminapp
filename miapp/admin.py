from django.contrib import admin
from .models import Producto, Cliente, Turno, ProductoSeleccionado,Carrito,Categoria,Articulo

# Define the admin interface for Producto
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio','categoria','descripcion', 'created', 'updated', 'image1', 'image2', 'image3', 'image4')
    list_filter = ('nombre', 'created')
    ordering = ('nombre',)

# Define the admin interface for Cliente
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'domicilio', 'Preferencia')

class TurnoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'productos_list', 'detalle_productos_admin', 'fecha_hora', 'duracion', 'created', 'updated')
    filter_horizontal = ('productos',)
    readonly_fields = ['detalle_productos']

    def productos_list(self, obj):
        return ", ".join([p.nombre for p in obj.productos.all()])
    productos_list.short_description = 'Productos'

    def detalle_productos_admin(self, obj):
        return obj.detalle_productos if obj.detalle_productos else 'Sin detalle'
    detalle_productos_admin.short_description = 'Detalle con Cantidades'

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

# Define the admin interface for Cliente
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'stock', 'categoria', 'fecha_creacion')
    list_filter = ('categoria', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    ordering = ('-fecha_creacion',)
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'precio', 'stock', 'categoria')
        }),
        ('Imágenes', {
            'fields': ('image1', 'image2', 'image3', 'image4', 'image5', 'image6')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion',)
        }),
    )

admin.site.register(Articulo, ArticuloAdmin)






# Register the models with the admin interface
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Turno, TurnoAdmin)
admin.site.register(ProductoSeleccionado, ProductoSeleccionadoAdmin)
admin.site.register(Carrito, CarritoAdmin)
admin.site.register(Categoria, CategoriaAdmin)