from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    
    class Meta:
        model = Producto
        fields = ['nombre','precio','duracion',]
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Productos'}),
            'precio': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Precio Unitario'}),
            'duracion': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Tiempo Duracion'}),
        }