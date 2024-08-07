import calendar
from collections import defaultdict
import datetime
from gettext import translation
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView, FormView, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.timezone import now
from django.db.models import F
from .models import *
from .forms import *


# Create your views here.
@method_decorator(login_required, name='dispatch')
class HomreView(TemplateView):
    template_name = "miapp/home.html"
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('restricted')  #  de definir esta URL en tus URLs
        return super().dispatch(request, *args, **kwargs)


class HomeViewVentas(TemplateView):
    template_name = "miapp/home_ventas.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.all()
        context['clientes'] = Cliente.objects.all()
        context['turnos'] = Turno.objects.all()
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = Carrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto
        return context


class MyLoginView(LoginView):
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home_ventas')
    
    def form_invalid(self, form):
        messages.error(self.request, "Usuario o contraseña invalidos") 
        return self.render_to_response(self.get_context_data(form=form))



class EliminarDelCarritoView(View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        try:
            item = Carrito.objects.get(id=item_id)
            item.delete()
        except Carrito.DoesNotExist:
            pass
        return redirect('crear_turno')    

class TurnoDetailView(DetailView):
    model = Turno
    template_name = 'miapp/turno_detail.html'
    context_object_name = 'turno'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        turno = self.get_object()
        
        context['cliente'] = turno.cliente
        context['productos'] = turno.productos.all()
        return context
class PaymentView(TemplateView):
    template_name = 'miapp/payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        # Procesa la solicitud GET
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        payment_data = request.POST.get('paymentData')
        
     
        return redirect('success')  

class RestrictedPageView(TemplateView):
    template_name = 'miapp/restricted_page.html'

class PaymentSuccessView(TemplateView):
    template_name = 'miapp/success.html'

@method_decorator(login_required, name='dispatch')
class AgendaView(TemplateView):
    template_name = 'miapp/agenda.html'
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('restricted')  
        return super().dispatch(request, *args, **kwargs)




    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener la fecha actual
        today = now().date()

        # Determinar el mes y el año a mostrar
        current_month = int(self.request.GET.get('month', today.month))
        current_year = int(self.request.GET.get('year', today.year))

        # Calcular el rango de fechas para el mes seleccionado
        start_date = f'{current_year}-{current_month:02d}-01'
        # Determinar el último día del mes
        next_month = current_month + 1
        if next_month > 12:
            next_month = 1
            next_year = current_year + 1
        else:
            next_year = current_year
        end_date = f'{next_year}-{next_month:02d}-01'

        # Obtener todos los turnos para el mes y año actuales
        turnos = Turno.objects.filter(
            fecha_hora__range=[start_date, end_date]
        ).order_by('fecha_hora')

        # Crear un diccionario para almacenar los turnos agrupados por fecha
        turnos_por_dia = {}
        for turno in turnos:
            fecha = turno.fecha_hora.date()
            if fecha not in turnos_por_dia:
                turnos_por_dia[fecha] = []
            turnos_por_dia[fecha].append(turno)

        # Preparar el calendario para todos los meses del año
        cal = calendar.Calendar(firstweekday=0)  # Semana comienza en lunes
        month_days_list = [(month, cal.monthdayscalendar(current_year, month)) for month in range(1, 13)]

        # Nombres de los meses en castellano
        month_names_es = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]

        # Calcular el rango de meses para la navegación
        months = [(current_year, month) for month in range(1, 13)]

        # Preparar nombres de los meses para el template
        months_with_names = [(month, month_names_es[month - 1]) for _, month in months]

        # Obtener el nombre del mes actual
        current_month_name = month_names_es[current_month - 1]

        # Obtener el turno más cercano para cada día
        turnos_mas_cercanos = {}
        for fecha, turnos_del_dia in turnos_por_dia.items():
            turnos_mas_cercanos[fecha] = min(turnos_del_dia, key=lambda t: t.fecha_hora)

        context['turnos_por_dia'] = turnos_por_dia
        context['turnos_mas_cercanos'] = turnos_mas_cercanos
        context['month_days_list'] = month_days_list
        context['months'] = months
        context['current_month'] = current_month
        context['current_year'] = current_year
        context['months_with_names'] = months_with_names  # Pasar los meses con nombres al contexto
        context['current_month_name'] = current_month_name  # Pasar el nombre del mes actual al contexto

        return context
    
class ConfirmacionTurnoView(TemplateView):
    template_name = 'miapp/confirmacion_turno.html'


        
        
    
@method_decorator(login_required, name='dispatch')
class CrearTurnoView(View):
    template_name = 'miapp/crear_turno.html'

    def get(self, request, *args, **kwargs):
        # Initialize forms
        form = TurnoForm()
        fecha_hora_form = TurnoFechaHoraForm()

        usuario = request.user

        miCarrito = Carrito.objects.filter(usuario=usuario).select_related('producto')
        
        # Calculate total duration
        total_duracion = sum(item.producto.duracion * item.cantidad for item in miCarrito)
        if self.request.user.is_authenticated:
            cantidad_en_carrito = Carrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0

        context = {
            'form': form,
            'fecha_hora_form': fecha_hora_form,
            'miCarrito': miCarrito,
            'total_duracion': total_duracion,
            'cantidad_en_carrito': cantidad_en_carrito,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        # Initialize forms
        form = TurnoDurationForm(request.POST)
        fecha_hora_form = TurnoFechaHoraForm(request.POST)

        if form.is_valid() and fecha_hora_form.is_valid():
            usuario = request.user
            duracion = form.cleaned_data['duracion']
            fecha_hora = fecha_hora_form.cleaned_data['fecha_hora']

            # Retrieve selected products from the user's cart
            miCarrito = Carrito.objects.filter(usuario=usuario).select_related('producto')
            if not miCarrito.exists():
                messages.error(request, 'No tienes productos en el carrito para crear un turno.')
                return self.render_form(form, fecha_hora_form, 'No tienes productos en el carrito para crear un turno.')

            # Verify the calculated total duration
            total_duracion = sum(item.producto.duracion * item.cantidad for item in miCarrito)

            if duracion != total_duracion:
                messages.error(request, 'La duración total del turno no coincide con la duración de los productos en el carrito.')
                return self.render_form(form, fecha_hora_form, 'La duración total del turno no coincide con la duración de los productos en el carrito.')

            # Create the turno
            with transaction.atomic():
                turno = Turno.objects.create(cliente=usuario, duracion=duracion, fecha_hora=fecha_hora)
                productos = [item.producto for item in miCarrito]
                turno.productos.set(productos)
                miCarrito.delete()

                # Handle payment options
                accion = request.POST.get('accion')
                if accion == 'pagar_local':
                    # Handle local payment logic (if needed)
                    messages.success(request, 'Turno creado exitosamente. Por favor, paga en el local.')
                    return redirect('confirmacion_turno')  # Redirect to the payment page
                elif accion == 'pagar_externo':
                    # Redirect to external payment page (if applicable)
                    messages.success(request, 'Turno creado exitosamente. Serás redirigido a la página de pago externo.')
                    return redirect('payment')  # Redirect to the payment page

                messages.success(request, 'Turno creado exitosamente.')
                return redirect(reverse_lazy('crear_turno'))
        else:
            print("Errores del formulario:", form.errors)
            print("Errores del formulario de fecha y hora:", fecha_hora_form.errors)
            return self.render_form(form, fecha_hora_form, 'Hubo un error en el formulario. Por favor, inténtalo de nuevo.')

    def render_form(self, form, fecha_hora_form, message):
        return render(self.request, self.template_name, {
            'form': form,
            'fecha_hora_form': fecha_hora_form,
            'message': message
        })
class AumentarCantidadView(View):
     def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        try:
            item = Carrito.objects.get(id=item_id)
            item.cantidad += 1
            item.save()
        except Carrito.DoesNotExist:
            pass
        return redirect('crear_turno')

class DisminuirCantidadView(View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        try:
            item = Carrito.objects.get(id=item_id)
            if item.cantidad > 0:
                item.cantidad -= 1
                item.save()
        except Carrito.DoesNotExist:
            pass
        return redirect('crear_turno')
        
class NoRegistradoView(TemplateView):
    template_name = 'miapp/no_registrado.html'

class RegistroUsuario(CreateView):
    model = User 
    template_name = "miapp/registro.html"
    form_class = UserCreationFormWithCliente
    success_url = reverse_lazy('home')  


class AgregarAlCarritoView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes estar registrado para agregar productos al carrito.')
            return redirect('no_registrado')  # Redirige a la página no_registrado.html

        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 1))  # Obtén la cantidad del formulario, con un valor predeterminado de 1

        producto = get_object_or_404(Producto, id=producto_id)
        usuario = request.user

        # Verifica si el producto ya está en el carrito del usuario
        carrito_item, creado = Carrito.objects.get_or_create(
            usuario=usuario,
            producto=producto,
            defaults={'cantidad': cantidad}
        )

        if not creado:
            carrito_item.cantidad += cantidad
            carrito_item.save()

        messages.success(request, 'Producto agregado al carrito.')
        return redirect('home_ventas')  # Redirige a la vista deseada
    
# views.py
class ConfirmarTurnoView(FormView):
    template_name = 'miapp/confirmar_turno.html'
    form_class = TurnoForm
    success_url = reverse_lazy('turno_confirmado')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos_seleccionados'] = ProductoSeleccionado.objects.filter(user=self.request.user)
        return context

    def form_valid(self, form):
        # Aquí puedes realizar la lógica para crear el turno y asociar los productos seleccionados
        ProductoSeleccionado.objects.filter(user=self.request.user).delete()
        return super().form_valid(form)

class ProductSearchView(ListView):
    model = Producto
    template_name = 'miapp/search_results.html'
    context_object_name = 'productos'

    def get_queryset(self):
        query = self.request.GET.get('nombre', '')
        if query:
            return Producto.objects.filter(nombre__icontains=query)
        return Producto.objects.all()
    
# [------------------------ SE CREAN LAS LISTAS PARA VER LOS MODELOS (LISTADOS DE REGISTROS)--------------------------------]    
@method_decorator(login_required, name='dispatch')
class ProductoList(ListView):    
    model = Producto
    
    def get_queryset(self):
        return Producto.objects.all().order_by('id').values()
        #return Producto.objects.filter(nombre__icontains='a').values()
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Listado Productos"
        return contexto
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('restricted')  
        return super().dispatch(request, *args, **kwargs)

class ClienteList(ListView):
    model = Cliente
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Listado Clientes"
        # Ejemplo de como podemos traer al  contexto de del html todos los productos
        # contexto['productos'] = Producto.objects.all().values()
        return contexto
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('restricted')  
        return super().dispatch(request, *args, **kwargs)

    
    
class TurnoList(ListView):
    model = Turno   
    template_name = 'miapp/turno_list.html'  
    context_object_name = 'object_list' 
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Listado Turnos"
        return contexto
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('restricted')  
        return super().dispatch(request, *args, **kwargs)
    
    
class CategoriaListView(ListView):
    model = Categoria
    template_name = 'miapp/categoria_list.html'  # Ruta al archivo de plantilla
    context_object_name = 'categorias'  # Nombre del contexto para la plantilla

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Lista de Categorías"
        return contexto

# [------------------------ SE CREAN LAS LISTAS PARA INGRESAR LOS MODELOS (ALTA DE REGISTROS)---------------------------------------]   
class ProductoCreate(CreateView):
       model = Producto
       form_class = ProductoForm
       success_url = reverse_lazy('producto')# Redirigimos cuando se registra
       
class ClienteCreate(CreateView):
    form_class = UserCreationFormWithCliente
    template_name = 'miapp/cliente_form.html'
    success_url = reverse_lazy('cliente')  

    def form_valid(self, form):
        username = form.cleaned_data['username']
        
        # Verificar si el nombre de usuario ya existe
        if User.objects.filter(username=username).exists():
            form.add_error('username', 'Este nombre de usuario ya está en uso.')
            return self.form_invalid(form)

        try:
            # Primero guarda el formulario que crea el usuario
            user = form.save()
            
            # Ahora crea el cliente asociado al usuario
            Cliente.objects.create(
                user=user,
                nombre=form.cleaned_data['nombre'],
                telefono=form.cleaned_data['telefono'],
                domicilio=form.cleaned_data['domicilio'],
                Preferencia=form.cleaned_data['Preferencia']
            )
        except IntegrityError as e:
            form.add_error(None, f'Error al crear el usuario o cliente: {e}')
            return self.form_invalid(form)

        return super().form_valid(form)
    
    
class TurnoCreate(CreateView):
    model = Turno
    form_class = TurnoForm
    success_url = reverse_lazy('turno')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.all()  # Pasar todos los productos al contexto
        return context


class CategoriaCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'miapp/categoria_form.html'
    success_url = reverse_lazy('home')  # Redirige a la lista de categorías después de crear

    def form_valid(self, form):
        # Aquí puedes agregar lógica adicional antes de guardar el formulario, si es necesario
        return super().form_valid(form)


# [------------------------ SE CREAN LAS LISTAS PARA ACTUALIZAR LOS MODELOS (MODIFICACIÓN DE REGISTROS)-----------------------------]       
class ProductoUpdate(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name_suffix = "_update_form"      
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Modificar Producto" # Establecemos el titulo del html
        return contexto
    def get_success_url(self):
        return reverse_lazy('producto_update',args=[self.object.id])+'?ok'

class ClienteUpdate(UpdateView):
    model = Cliente
    form_class = UserCreationFormWithCliente
    template_name_suffix = "_update_form"      
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Modificar Cliente" # Establecemos el titulo del html
        return contexto
    def get_success_url(self):
        return reverse_lazy('cliente_update',args=[self.object.id])+'?ok'

class TurnoUpdate(UpdateView):
    model = Turno
    form_class = TurnoForm
    template_name_suffix = "_update_form"      


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['duracion_form'] = TurnoDurationForm()  # Agrega el formulario de duración al contexto
        context['titulo'] = "Modificar Turno"  # Establece el título del HTML
        return context

    def post(self, request, *args, **kwargs):
        turno_form = TurnoForm(request.POST, instance=self.get_object())
        duracion_form = TurnoDurationForm(request.POST)

        if turno_form.is_valid() and duracion_form.is_valid():
            response = super().post(request, *args, **kwargs)

            # Procesa el formulario de duración adicional
            turno = self.get_object()
            duracion = duracion_form.cleaned_data['duracion']
            turno.duracion = duracion
            turno.save()

            messages.success(request, 'Turno actualizado exitosamente.')
            return response
        else:
            return self.render_to_response(self.get_context_data(turno_form=turno_form, duracion_form=duracion_form))

    def get_success_url(self):
        return reverse_lazy('turno_update', args=[self.object.id]) + '?ok'
# [------------------------ SE CREAN LAS LISTAS PARA ELIMINAR LOS MODELOS (ELIMINACIÓN DE REGISTROS)--------------------------------]   
class ProductoDelete(DeleteView):
    model = Producto
    success_url = reverse_lazy('producto')    
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Eliminar Producto"
        return contexto

class ClienteDelete(DeleteView):
    model = Cliente
    success_url = reverse_lazy('cliente')    
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Eliminar Cliente"
        return contexto    

class TurnoDelete(DeleteView):
    model = Turno
    success_url = reverse_lazy('turno')    
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Eliminar Turno"
        return contexto    
       
    
    