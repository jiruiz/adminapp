from django import forms
from .models import Producto,Cliente,Turno
# se debe instalar el ckeditor (pip install django-ckeditor)
from ckeditor.widgets import CKEditorWidget

class ProductoForm(forms.ModelForm):
    
    class Meta:
        model = Producto
        fields = ['nombre','precio','duracion','image1','image2','image3','image4',]
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Productos'}),
            'precio': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Precio Unitario'}),
            'duracion': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Tiempo Duracion'}),
            'image1': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image3': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image4': forms.ClearableFileInput(attrs={'class': 'form-control'}),
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
        

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['cliente', 'productos', 'duracion']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'productos': forms.CheckboxSelectMultiple(),  # Sin CSS aquí
            'duracion': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duración en minutos'}),
        }