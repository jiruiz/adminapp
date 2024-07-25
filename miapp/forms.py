from django import forms
from .models import Producto,Cliente
# se debe instalar el ckeditor (pip install django-ckeditor)
from ckeditor.widgets import CKEditorWidget

class ProductoForm(forms.ModelForm):
    
    class Meta:
        model = Producto
        fields = ['nombre','precio','duracion',]
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Productos'}),
            'precio': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Precio Unitario'}),
            'duracion': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Tiempo Duracion'}),
        }
        
        
class ClienteForm(forms.ModelForm):
    
    class Meta:
        model = Cliente
        fields = ['nombre','telefono','domicilio', 'Preferencia',]
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Nombre'}),
            'telefono': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Telefono'}),
            'domicilio': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Domicilio'}),
            'Preferencia': CKEditorWidget(),
        }        