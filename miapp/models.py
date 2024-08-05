from django.db import models
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.utils import timezone


# Define the Producto model
class Producto(models.Model):
    nombre = models.CharField(verbose_name="Producto", max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.IntegerField()
    image1 = models.ImageField(upload_to="productos", null=True, blank=True, verbose_name="Ilustración 1")
    image2 = models.ImageField(upload_to="productos", null=True, blank=True, verbose_name="Ilustración 2")
    image3 = models.ImageField(upload_to="productos", null=True, blank=True, verbose_name="Ilustración 3")
    image4 = models.ImageField(upload_to="productos", null=True, blank=True, verbose_name="Ilustración 4")
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre}"
    
    
    #lo siguiente mostraria ordenado por nombre y tambien solo una cantidad de caracteres (2) 
    # @admin.display(ordering="nombre")
    # def nombrePresentacion(self):
    #     return format_html(self.nombre[:2]+"...")
        
class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    nombre = models.CharField(verbose_name="Cliente", max_length=50)
    telefono = models.CharField(max_length=16)
    domicilio = models.CharField(max_length=50)
    Preferencia = models.TextField(verbose_name="Preferencia")

    def __str__(self):
        return f"{self.nombre}"


# Define the Turno model
class Turno(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='turnos')
    productos = models.ManyToManyField(Producto, related_name='turnos')
    duracion = models.IntegerField()  # Representa minutos
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    fecha_hora = models.DateTimeField(default=timezone.now)  # Combina fecha y hora

    def __str__(self):
        return f"Turno {self.id} - Cliente: {self.cliente.username}"

    def productos_list(self):
        return ", ".join([producto.nombre for producto in self.productos.all()])
    productos_list.short_description = 'Productos'
    
class ProductoSeleccionado(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_seleccion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"    
    
    
class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"

    @property
    def subtotal(self):
        return self    
    
    
