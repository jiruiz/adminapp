from django.contrib import admin
from .models import *
# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    # readonly_fields=('created','updated')
    list_display=('nombre','precio','created','updated')
    list_filter = ('nombre','created',)
    ordering=('nombre',)

admin.site.register(Producto,ProductoAdmin)


