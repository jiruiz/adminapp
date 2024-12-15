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

        # Agrupa productos por categoría
        context['productos_por_categoria'] = Producto.objects.values('categoria__nombre').distinct()
        
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = Carrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito
        # Generar nombres para los indicadores del carrusel
        context['nombres_indicadores'] = [
            producto.nombre for idx, producto in enumerate(context['productos']) if idx % 4 == 0
        ]
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
    
    
class PeluqueriaListView(TemplateView):
    template_name = 'miapp/peluqueria.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filtrar los artículos por la categoría "Peluquería"
        # Asegúrate de que el nombre de la categoría "Peluquería" existe en la base de datos
        categoria_peluqueria = Categoria.objects.get(nombre='Peluquería')
        pelu = Producto.objects.filter(categoria=categoria_peluqueria)
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = Carrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto
        context['peluqueria'] = pelu
        return context

class ManicuriaListView(TemplateView):
    template_name = 'miapp/manicuria.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filtrar los artículos por la categoría "Peluquería"
        # Asegúrate de que el nombre de la categoría "Peluquería" existe en la base de datos
        categoria_manicuria = Categoria.objects.get(nombre='Manicuría')
        pelu = Producto.objects.filter(categoria=categoria_manicuria)
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = Carrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto
        context['manicuria'] = pelu
        return context
        
    
    
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
    
class TurnoDetailClienteView(DetailView):
    model = Turno
    template_name = 'miapp/turno_detail_cliente.html'
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

        today = now().date()
        current_month = int(self.request.GET.get('month', today.month))
        current_year = int(self.request.GET.get('year', today.year))
        current_day = int(self.request.GET.get('day', today.day)) if self.request.GET.get('day') else None
        current_hour = self.request.GET.get('hour')

        # Cálculo de las fechas de inicio y fin del mes actual
        start_date = f'{current_year}-{current_month:02d}-01'
        next_month = current_month + 1
        next_year = current_year if next_month <= 12 else current_year + 1
        next_month = next_month if next_month <= 12 else 1
        end_date = f'{next_year}-{next_month:02d}-01'

        # Filtro básico de mes y año
        turnos = Turno.objects.filter(
            fecha_hora__range=[start_date, end_date]
        ).order_by('fecha_hora')

        # Filtrar por día si está presente
        if current_day:
            turnos = turnos.filter(fecha_hora__day=current_day)

        # Filtrar por hora si está presente
        if current_hour:
            turnos = turnos.filter(fecha_hora__time=current_hour)

        turnos_por_dia = {}
        for turno in turnos:
            fecha = turno.fecha_hora.date()
            turnos_por_dia.setdefault(fecha, []).append(turno)

        cal = calendar.Calendar(firstweekday=0)
        month_days_list = [(month, cal.monthdayscalendar(current_year, month)) for month in range(1, 13)]

        month_names_es = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]

        months = [(current_year, month) for month in range(1, 13)]
        months_with_names = [(month, month_names_es[month - 1]) for _, month in months]
        current_month_name = month_names_es[current_month - 1]

        turnos_mas_cercanos = {
            fecha: min(turnos_del_dia, key=lambda t: t.fecha_hora)
            for fecha, turnos_del_dia in turnos_por_dia.items()
        }

        context.update({
            'turnos_por_dia': turnos_por_dia,
            'turnos_mas_cercanos': turnos_mas_cercanos,
            'month_days_list': month_days_list,
            'months': months,
            'current_month': current_month,
            'current_year': current_year,
            'current_day': current_day,
            'current_hour': current_hour,
            'months_with_names': months_with_names,
            'current_month_name': current_month_name,
        })
        return context

class ConfirmacionTurnoView(TemplateView):
    template_name = 'miapp/confirmacion_turno.html'
        
        
from datetime import datetime, timedelta

class CrearTurnoView(View):
    template_name = 'miapp/crear_turno.html'

    def get(self, request, *args, **kwargs):
        form = TurnoForm()
        fecha_hora_form = TurnoFechaHoraForm()

        usuario = request.user
        miCarrito = Carrito.objects.filter(usuario=usuario).select_related('producto')
        
        total_duracion = sum(item.producto.duracion * item.cantidad for item in miCarrito)
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
        form = TurnoDurationForm(request.POST)
        fecha_hora_form = TurnoFechaHoraForm(request.POST)

        if form.is_valid() and fecha_hora_form.is_valid():
            usuario = request.user
            duracion = form.cleaned_data['duracion']
            fecha_hora = fecha_hora_form.cleaned_data['fecha_hora']

            # Depuración
            print("fecha_hora:", fecha_hora)
            print("duracion:", duracion)

            # Asegurarse de que 'fecha_hora' es un datetime
            if isinstance(fecha_hora, str):
                fecha_hora = datetime.strptime(fecha_hora, '%Y-%m-%d %H:%M')  # Ajusta el formato si es necesario

            # Asegurarse de que 'duracion' es un entero
            duracion = int(duracion)

            miCarrito = Carrito.objects.filter(usuario=usuario).select_related('producto')
            if not miCarrito.exists():
                messages.error(request, 'No tienes productos en el carrito para crear un turno.')
                return self.render_form(form, fecha_hora_form, 'No tienes productos en el carrito para crear un turno.')

            total_duracion = sum(item.producto.duracion * item.cantidad for item in miCarrito)

            if duracion != total_duracion:
                messages.error(request, 'La duración total no coincide con los productos en el carrito.')
                return self.render_form(form, fecha_hora_form, 'La duración total no coincide con los productos en el carrito.')

            # Verificar si el nuevo turno se solapa con algún turno existente
            fecha_hora_fin = fecha_hora + timedelta(minutes=duracion)
            turnos_solapados = Turno.objects.filter(
                fecha_hora__lt=fecha_hora_fin,
                fecha_hora__gte=fecha_hora
            ) | Turno.objects.filter(
                fecha_hora__lt=fecha_hora,
                fecha_hora__gte=fecha_hora - timedelta(minutes=duracion)
            )

            if turnos_solapados.exists():
                mensaje = 'El horario seleccionado se encuentra ocupado por turnos existentes. Por favor, elige otro horario.'
                return self.render_form(form, fecha_hora_form, mensaje, turnos_solapados)

            # Crear el nuevo turno
            Turno.objects.create(cliente=usuario, duracion=duracion, fecha_hora=fecha_hora)
            miCarrito.delete()
            messages.success(request, 'Turno creado exitosamente.')
            return redirect('success')  # Cambia esto a tu URL de éxito.

        return self.render_form(form, fecha_hora_form)

    def render_form(self, form, fecha_hora_form, mensaje=None, turnos_solapados=None):
        usuario = self.request.user
        miCarrito = Carrito.objects.filter(usuario=usuario).select_related('producto')
        total_duracion = sum(item.producto.duracion * item.cantidad for item in miCarrito)
        context = {
            'form': form,
            'fecha_hora_form': fecha_hora_form,
            'miCarrito': miCarrito,
            'total_duracion': total_duracion,
            'message': mensaje,
            'turnos_solapados': turnos_solapados,
        }
        return render(self.request, self.template_name, context)

class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'miapp/producto_detail.html'
    context_object_name = 'producto'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = f"Detalle de {self.object.nombre}"
        return contexto        
        
        
        
        
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
    success_url = reverse_lazy('login')  


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
    success_url = reverse_lazy('home')  

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
    
from datetime import datetime, timedelta
from django.contrib import messages

class TurnoCreate(CreateView):
    model = Turno
    form_class = TurnoForm
    success_url = reverse_lazy('turno')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.all()  # Pasar todos los productos al contexto

        # Verificar si hay turnos solapados
        fecha_hora = self.request.POST.get('fecha_hora')
        if fecha_hora:
            try:
                # Convertir fecha_hora a datetime (el formato correcto debe ser '%Y-%m-%d %H:%M')
                fecha_hora = datetime.strptime(fecha_hora, '%Y-%m-%d %H:%M')

                # Buscar turnos que solapan con la fecha y hora seleccionadas
                turnos_solapados = Turno.objects.filter(
                    fecha_hora__lt=fecha_hora + timedelta(minutes=30),
                    fecha_hora__gt=fecha_hora - timedelta(minutes=30)
                )

                # Si hay turnos solapados, pasarlos al contexto
                if turnos_solapados.exists():
                    context['turnos_solapados'] = turnos_solapados
                else:
                    context['turnos_solapados'] = None
            except ValueError:
                context['turnos_solapados'] = None

        return context

    def form_valid(self, form):
        # Validar si el turno ya existe para la fecha y hora seleccionadas
        fecha_hora = form.cleaned_data['fecha_hora']
        cliente = form.cleaned_data['cliente']

        # Verificar si ya existe un turno para esa fecha y hora
        turno_existente = Turno.objects.filter(fecha_hora=fecha_hora).exclude(cliente=cliente)
        if turno_existente.exists():
            form.add_error('fecha_hora', 'Ya existe un turno en esa fecha y hora.')
            return self.form_invalid(form)

        # Guardar el turno si no hay conflicto
        return super().form_valid(form)


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
       
    
# # ver compras por parte del usuario 
# class VerMisTurnosView(LoginRequiredMixin, TemplateView):
#     template_name = 'miapp/ver_mis_turnos.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Agregar el objeto de usuario al contexto
#         context['usuario'] = self.request.user
        
#         # Obtén todas las compras del usuario actual, ordenadas por fecha de manera descendente
#         turnos = Turno.objects.filter(usuario=self.request.user).order_by('-fecha')
#         cantidad_en_carrito = 0
#         if self.request.user.is_authenticated:
#             cantidad_en_carrito = Carrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
#         context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto
#         context['turnos'] = turnos
#         return context
    
    
    
class VerMisTurnosView(LoginRequiredMixin, TemplateView):
    template_name = 'miapp/ver_mis_turnos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el usuario actual
        usuario = self.request.user
        context['usuario'] = usuario
        
        # Obtener todos los turnos del usuario actual, ordenados por fecha de manera descendente
        turnos = Turno.objects.filter(cliente=usuario).order_by('-fecha_hora')
        context['turnos'] = turnos
        
        # Calcular el total de productos en el carrito del usuario actual
        cantidad_en_carrito = Carrito.objects.filter(usuario=usuario).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito
        
        return context




# # -----perfil de usuario
# class PerfilView(DetailView):
#     model = Cliente
#     template_name = 'perfil.html'  # Asegúrate de que esta plantilla exista
#     context_object_name = 'cliente'

#     def get_object(self):
#         # Obtiene el usuario actual
#         user = self.request.user
#         # Obtiene el objeto Cliente relacionado con el usuario
#         return get_object_or_404(Cliente, user=user)