import calendar
from collections import defaultdict
import datetime
from gettext import translation
from urllib import request
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
from django.contrib.auth import update_session_auth_hash



def inicio(request):
    return render(request, 'miapp/inicio.html')

@method_decorator(login_required, name='dispatch')
class HomreView(TemplateView):
    template_name = "miapp/home.html"
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('restricted')  #  de definir esta URL en tus URLs
        return super().dispatch(request, *args, **kwargs)

@login_required
def cambiar_clave(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Mantén la sesión activa
            return redirect('perfil_usuario')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'miapp/cambiar_clave.html', {'form': form})

@login_required
def perfil_usuario(request):
    # Obtén el usuario actual
    usuario = request.user  # El usuario autenticado
    # Accede a los datos del cliente relacionados con este usuario
    cliente = usuario.cliente  # El objeto Cliente relacionado con el usuario

    # Pasa los datos a la plantilla
    return render(request, 'miapp/perfil_usuario.html', {'usuario': usuario, 'cliente': cliente})

@login_required
def editar_perfil(request):
    usuario = request.user  # El usuario autenticado
    cliente = usuario.cliente  # El objeto Cliente relacionado con el usuario

    if request.method == 'POST':
        form = UserCreationFormWithCliente(request.POST, instance=usuario)
        cliente_form = ClienteForm(request.POST, instance=cliente)  # Asegúrate de tener un formulario para Cliente

        if form.is_valid() and cliente_form.is_valid():
            form.save(commit=False)  # No guardes los datos del usuario aún
            cliente_form.save()  # Guarda solo los datos del cliente
            return redirect('perfil_usuario')  # Redirige al perfil después de guardar los cambios
    else:
        form = UserCreationFormWithCliente(instance=usuario)
        cliente_form = ClienteForm(instance=cliente)

    return render(request, 'miapp/editar_perfil.html', {'form': form, 'cliente_form': cliente_form, 'cliente': cliente})

def base_ventas(request):
    # Obtener todas las categorías
    categorias = Categoria.objects.all().order_by('nombre').values_list('nombre').distinct()[:10]
    
    return render(request, 'base_ventas.html', {'categorias': categorias})

class HomeViewVentas(TemplateView):
    template_name = "miapp/home_ventas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.all()
        context['clientes'] = Cliente.objects.all()
        context['turnos'] = Turno.objects.all()
        context['titulo'] = 'Home'

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

from django.utils.timezone import make_aware



class CalendarView(TemplateView):
    template_name = 'miapp/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Recuperar todos los turnos sin restricciones de fecha
        turnos = Turno.objects.all().order_by('fecha_hora')

        # Agrupar turnos por día (opcional)
        turnos_por_dia = {}
        for turno in turnos:
            fecha = turno.fecha_hora.date()
            if fecha not in turnos_por_dia:
                turnos_por_dia[fecha] = []
            turnos_por_dia[fecha].append(turno)

        context.update({
            'turnos_por_dia': turnos_por_dia,
        })
        return context



class ConfirmacionTurnoView(TemplateView):
    template_name = 'miapp/confirmacion_turno.html'
        

from datetime import timedelta
from django.utils.timezone import make_aware, is_naive
from django.utils.timezone import now, localtime
from django.contrib import messages        
from datetime import datetime, timedelta
from django.utils.timezone import localtime

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

            # Asegurarse de que la fecha y hora sea "timezone-aware"
            if is_naive(fecha_hora):
                fecha_hora = make_aware(fecha_hora)

            print(f"Fecha y hora seleccionada (local): {localtime(fecha_hora)}")

            # Verificar si hay productos en el carrito
            miCarrito = Carrito.objects.filter(usuario=usuario).select_related('producto')
            if not miCarrito.exists():
                messages.error(request, 'No tienes productos en el carrito para crear un turno.')
                return self.render_form(form, fecha_hora_form, 'No tienes productos en el carrito para crear un turno.')

            # Calcular la duración total de los productos en el carrito
            total_duracion = sum(item.producto.duracion * item.cantidad for item in miCarrito)

            if duracion != total_duracion:
                messages.error(request, 'La duración total no coincide con los productos en el carrito.')
                return self.render_form(form, fecha_hora_form, 'La duración total no coincide con los productos en el carrito.')

            # Determinar el rango del turno solicitado
            fecha_hora_inicio = fecha_hora.replace(minute=0, second=0, microsecond=0)
            fecha_hora_fin = fecha_hora_inicio + timedelta(minutes=duracion)

            # Verificar si el nuevo turno está dentro del horario de atención
            horario_apertura = 9  # Hora de apertura (9:00 AM)
            horario_cierre = 19   # Hora de cierre (7:00 PM)

            if fecha_hora_inicio.hour < horario_apertura or (fecha_hora_fin.hour >= horario_cierre and fecha_hora_fin.minute > 0):
                messages.error(request, f'El horario de atención es de {horario_apertura}:00 a {horario_cierre}:00. Por favor, elige un horario dentro del horario de atención.')
                return self.render_form(form, fecha_hora_form, f'El horario de atención es de {horario_apertura}:00 a {horario_cierre}:00. Por favor, elige un horario dentro del horario de atención.')

            # Verificar si el nuevo turno solapa con alguno ya existente
            solapado = Turno.objects.filter(
                fecha_hora__lt=fecha_hora_fin,
                fecha_hora__gte=fecha_hora_inicio
            ).exists()

            if solapado:
                # Buscar los turnos solapados
                turnos_solapados = Turno.objects.filter(
                    fecha_hora__lt=fecha_hora_fin,
                    fecha_hora__gte=fecha_hora_inicio
                )
                mensaje = 'El horario seleccionado está ocupado por los siguientes turnos:'
                for turno in turnos_solapados:
                    turno_local = localtime(turno.fecha_hora)
                    mensaje += f'\n- Fecha y Hora: {turno_local.strftime("%d de %B de %Y a las %H:%M")} - Duración: {turno.duracion} minutos'

                # Calcular el próximo horario disponible del mismo día
                proximo_horario_disponible = None
                turnos_del_dia = Turno.objects.filter(fecha_hora__date=fecha_hora.date()).order_by('fecha_hora')
                for i in range(len(turnos_del_dia) - 1):
                    if turnos_del_dia[i + 1].fecha_hora > turnos_del_dia[i].fecha_hora + timedelta(minutes=turnos_del_dia[i].duracion + duracion):
                        proximo_horario_disponible = turnos_del_dia[i].fecha_hora + timedelta(minutes=turnos_del_dia[i].duracion)
                        break

                if not proximo_horario_disponible:
                    ultimo_turno_dia = turnos_del_dia.last()
                    if ultimo_turno_dia:
                        proximo_horario_disponible = ultimo_turno_dia.fecha_hora + timedelta(minutes=ultimo_turno_dia.duracion)

                if proximo_horario_disponible:
                    proximo_horario = localtime(proximo_horario_disponible).strftime("%d de %B de %Y a las %H:%M")
                    mensaje += f'\nEl próximo horario disponible del mismo día es: {proximo_horario}\n'
                else:
                    mensaje += '\nNo se encontró un próximo horario disponible del mismo día.'

                # Mostrar horarios disponibles de la semana
                start_week = fecha_hora - timedelta(days=fecha_hora.weekday())
                end_week = start_week + timedelta(days=6)
                turnos_semana = Turno.objects.filter(fecha_hora__range=[start_week, end_week]).order_by('fecha_hora')

                mensaje += '\nHorarios disponibles de la semana:'
                horarios_disponibles_semana = []
                for i in range(len(turnos_semana) - 1):
                    if turnos_semana[i + 1].fecha_hora > turnos_semana[i].fecha_hora + timedelta(minutes=turnos_semana[i].duracion + duracion):
                        horario_disponible = turnos_semana[i].fecha_hora + timedelta(minutes=turnos_semana[i].duracion)
                        horarios_disponibles_semana.append(localtime(horario_disponible).strftime("%d de %B de %Y a las %H:%M"))

                if horarios_disponibles_semana:
                    mensaje += "\n- " + "\n- ".join(horarios_disponibles_semana)
                else:
                    mensaje += '\nNo se encontraron horarios disponibles en la semana.'

                print(f"Mensaje de advertencia: {mensaje}")

                messages.error(request, mensaje)
                return self.render_form(form, fecha_hora_form, mensaje, turnos_solapados)

            # Crear el turno si no hay solapamientos
            turno = Turno.objects.create(cliente=usuario, duracion=duracion, fecha_hora=fecha_hora_inicio)
            print(f"Turno creado: {turno}")

            # Asociar productos y limpiar carrito
            for item in miCarrito:
                turno.productos.add(item.producto)
                item.delete()

            messages.success(request, 'Turno creado exitosamente.')
            return redirect('success')

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






def editar_turno(request, turno_id):
    # Obtener el turno correspondiente o redirigir si no existe
    turno = get_object_or_404(Turno, id=turno_id)
    
    # Si el formulario es enviado (es una solicitud POST)
    if request.method == 'POST':
        form = TurnoForm(request.POST, instance=turno)
        if form.is_valid():
            form.save()  # Guardar los cambios en el modelo
            return redirect('lista_turnos')  # Redirige a la lista de turnos (o donde prefieras)
    else:
        # Si no es una solicitud POST, simplemente mostrar el formulario con los datos actuales
        form = TurnoForm(instance=turno)
    
    return render(request, 'miapp/editar_turno.html', {'form': form, 'turno': turno})



class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'miapp/producto_detail.html'
    context_object_name = 'producto'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = 'Detalle'
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = Carrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        contexto['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto
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
    success_url = reverse_lazy('registro_exitoso')  

class RegistroExitoso(TemplateView):
    template_name = "miapp/registro_exitoso.html"




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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = Carrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito
        return context
    
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

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = "Eliminar Turno"
        contexto['template_base'] = 'miapp/base.html' if self.request.user.is_staff else 'miapp/base_ventas.html'
        return contexto

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('turno')  # Redirige a la lista de turnos general
        else:
            return reverse_lazy('ver_mis_turnos')  # Redirige a la lista de turnos del usuario

    def form_valid(self, form):
        # Redirigir a una página de confirmación después de eliminar
        messages.success(self.request, "El turno fue eliminado con éxito.")
        return super().form_valid(form)   
    
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

        # Recuperar los turnos del cliente logueado, ordenados por fecha
        if usuario.is_staff:
            turnos = Turno.objects.all().order_by('fecha_hora')
        else:
            turnos = Turno.objects.filter(cliente=usuario).order_by('fecha_hora')

        cantidad_en_carrito = Carrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        
        # Agrupar turnos por día
        turnos_por_dia = {}
        for turno in turnos:
            fecha = turno.fecha_hora.date()
            if fecha not in turnos_por_dia:
                turnos_por_dia[fecha] = []
            turnos_por_dia[fecha].append(turno)

        # Obtener los productos asociados a cada turno (si existe la relación)
        for turno in turnos:
            turno.productos_list = turno.productos.all()  # Si tienes esta relación, ajusta el nombre del campo

        context.update({
            'turnos_por_dia': turnos_por_dia,
            'cantidad_en_carrito': cantidad_en_carrito,
            'turnos': turnos,
            'es_staff': usuario.is_staff  # Añadir información sobre si el usuario es staff
        })

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


class VerCalendarioTurnosView(LoginRequiredMixin, TemplateView):
    template_name = 'miapp/calendario_turnos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el usuario actual
        usuario = self.request.user

        # Recuperar los turnos del cliente logueado, ordenados por fecha
        turnos = Turno.objects.filter(cliente=usuario).order_by('fecha_hora')

        # Agrupar turnos por día
        turnos_por_dia = {}
        for turno in turnos:
            fecha = turno.fecha_hora.date()
            if fecha not in turnos_por_dia:
                turnos_por_dia[fecha] = []
            turnos_por_dia[fecha].append(turno)

        # Obtener los productos asociados a cada turno (si existe la relación)
        for turno in turnos:
            # Asegúrate de que 'productos' sea el nombre del campo en el modelo
            turno.productos_list = turno.productos.all()

        context.update({
            'turnos_por_dia': turnos_por_dia,
            'turnos': turnos,
        })

        return context




# Vista para crear un artículo
def crear_articulo(request):
    if request.method == 'POST':
        form = ArticuloForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('miapp/lista_articulos.html')  # Redirige a la misma página para seguir creando artículos
    else:
        form = ArticuloForm()
    
    context = {
        'form': form,
    }
    return render(request, 'miapp/crear_articulo.html', context)



def editar_articulo(request, id):
    articulo = get_object_or_404(Articulo, id=id)
    
    if request.method == "POST":
        form = ArticuloForm(request.POST, instance=articulo)
        if form.is_valid():
            form.save()
            return redirect('lista_articulos')  # Redirigir a la lista de artículos
    else:
        form = ArticuloForm(instance=articulo)

    return render(request, 'miapp/editar_articulo.html', {'form': form, 'articulo': articulo})



def lista_articulos(request):
    articulos = Articulo.objects.all()
    return render(request, 'miapp/lista_articulos.html', {'articulos': articulos})