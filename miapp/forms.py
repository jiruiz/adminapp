from django import forms
from .models import Producto, Cliente, Turno, Categoria
from tinymce.widgets import TinyMCE
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'duracion', 'descripcion', 'categoria', 'image1', 'image2', 'image3', 'image4']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Productos'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio Unitario'}),
            'duracion': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tiempo Duracion'}),
            'descripcion': TinyMCE(attrs={'class': 'form-control', 'placeholder': 'Descripcion'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'image1': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image3': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image4': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class UserCreationFormWithCliente(UserCreationForm):
    nombre = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))
    telefono = forms.CharField(max_length=16, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefono'}))
    domicilio = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Domicilio'}))
    Preferencia = forms.CharField(widget=TinyMCE(attrs={'class': 'form-control', 'placeholder': 'Preferencia'}))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'nombre', 'telefono', 'domicilio', 'Preferencia']

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['cliente', 'productos', 'duracion', 'fecha_hora']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'productos': forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),
            'duracion': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duración en minutos', 'readonly': 'readonly'}),
            'fecha_hora': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar atributos personalizados a los campos, si es necesario
        self.fields['nombre'].label = 'Nombre de la Categoría'
        self.fields['nombre'].help_text = 'Ingrese el nombre de la categoría (máx. 100 caracteres).'    

class TurnoDurationForm(forms.Form):
    duracion = forms.IntegerField(label='Duración en minutos', min_value=1)

class TurnoFechaHoraForm(forms.Form):
    fecha_hora = forms.DateTimeField(
        label='Fecha y Hora',
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
    )
