import calendar
from collections import defaultdict
import datetime
from gettext import translation
from time import localtime
from urllib import request
from django.http import JsonResponse
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
from adminapp import settings

def inicio(request):
    # Obtenemos la cantidad total de productos en el carrito del usuario autenticado
    if request.user.is_authenticated:
        cantidad_en_carrito = Carrito.objects.filter(usuario=request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
    else:
        cantidad_en_carrito = 0

    context = {
        'cantidad_en_carrito': cantidad_en_carrito,
    }

    return render(request, 'miapp/inicio.html', context)
@method_decorator(login_required, name='dispatch')
class HomreView(TemplateView):
    template_name = "miapp/home.html"
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('restricted')  #  de definir esta URL en tus URLs
        return super().dispatch(request, *args, **kwargs)

@login_required
def cambiar_clave(request):
    usuario = request.user
    cantidad_en_carrito = Carrito.objects.filter(usuario=usuario).aggregate(Sum('cantidad'))['cantidad__sum'] or 0

    if request.method == 'POST':
        form = CustomPasswordChangeForm(usuario, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Mantiene sesión activa
            return redirect('perfil_usuario')
    else:
        form = CustomPasswordChangeForm(usuario)
    
    return render(request, 'miapp/cambiar_clave.html', {
        'form': form,
        'cantidad_en_carrito': cantidad_en_carrito
    })

@login_required
def perfil_usuario(request):
    usuario = request.user
    cliente = usuario.cliente

    # Cantidad total en carrito
    cantidad_en_carrito = Carrito.objects.filter(usuario=usuario).aggregate(Sum('cantidad'))['cantidad__sum'] or 0

    # Turnos del usuario, ordenados por fecha_hora
    turnos = Turno.objects.filter(cliente=usuario).order_by('fecha_hora')

    # Agrupar turnos por fecha
    turnos_por_dia = defaultdict(list)
    for turno in turnos:
        fecha = turno.fecha_hora.date()
        turnos_por_dia[fecha].append(turno)
        # Asegurarse que turno tenga lista de productos para mostrar en template
        turno.productos_list = [p.nombre for p in turno.productos.all()]

    # Productos seleccionados del usuario (si usas ese modelo)
    productos_seleccionados = ProductoSeleccionado.objects.filter(user=usuario)

    # Carrito del usuario
    carrito = Carrito.objects.filter(usuario=usuario)

    contexto = {
        'usuario': usuario,
        'cliente': cliente,
        'cantidad_en_carrito': cantidad_en_carrito,
        'turnos_por_dia': dict(turnos_por_dia),  # Convertir a dict para el template
        'productos_seleccionados': productos_seleccionados,
        'carrito': carrito,
    }

    return render(request, 'miapp/perfil_usuario.html', contexto)

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
        return redirect('guardar_turno')    
    
    
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


from django.utils.timezone import make_aware, is_naive
import mercadopago

class ConfirmacionTurnoView(TemplateView):
    template_name = 'miapp/confirmacion_turno.html'
        
from django.views import View
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
import mercadopago
from .models import Carrito
from django.contrib.auth import get_user_model

class IniciarPagoView(View):
    template_name = 'miapp/iniciar_pago.html'

    def get(self, request):
        turno_data = request.session.get('turno_data')
        if not turno_data:
            messages.error(request, "No hay datos de turno para procesar el pago.")
            return redirect('crear_turno')

        usuario_id = turno_data['usuario_id']
        User = get_user_model()
        try:
            usuario = User.objects.get(id=usuario_id)
        except User.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect('crear_turno')

        carrito = Carrito.objects.filter(usuario=usuario).select_related('producto')
        if not carrito.exists():
            messages.error(request, "El carrito está vacío.")
            return redirect('crear_turno')

        total_carrito = sum(item.producto.precio * item.cantidad for item in carrito)
        duracion = turno_data['duracion']

        mp = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

        items = [{
            "title": item.producto.nombre,
            "quantity": item.cantidad,
            "unit_price": float(item.producto.precio),
            "currency_id": "ARS"
        } for item in carrito]

        print("Items enviados a Mercado Pago:", items)
        success_url = "https://stunning-space-invention-pg55xx7xjx63qpj-8000.app.github.dev/success/"
        failure_url = "https://stunning-space-invention-pg55xx7xjx63qpj-8000.app.github.dev/failure/"
        pending_url = "https://stunning-space-invention-pg55xx7xjx63qpj-8000.app.github.dev/pending/"

        # Datos del comprador
        if request.user.is_authenticated:
            comprador_email = request.user.email  # Usamos el email del usuario autenticado
            print(f"Email del comprador: {comprador_email}")

        preference_data = {
            "items": items,
            "payer": {
                "email": usuario.email
            },
             "back_urls": {
                "success": success_url,  # Redirigir a la URL de éxito
                "failure": failure_url,  # Redirigir a la URL de fracaso
                "pending": pending_url,  # Redirigir a la URL de pendiente
            },
            "auto_return": "approved",  # 👈 redirección automática
            "external_reference": str(usuario.id),  # 👈 útil para verificar luego          
        }




        preference_response = mp.preference().create(preference_data)
        print("Respuesta de Mercado Pago:", preference_response)

        if preference_response["status"] != 201:
            # manejo de error...
            return redirect('crear_turno')

        preference_id = preference_response["response"]["id"]

        context = {
            'preference_id': preference_id,
            'public_key': settings.MERCADOPAGO_PUBLIC_KEY,
            'total_carrito': total_carrito,
            'duracion': duracion,
        }
        return render(request, self.template_name, context)



def verificar_pago(request):
    if not request.user.is_authenticated:
        return redirect('login')

    usuario = request.user
    mp = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    search_result = mp.payment().search({
        "external_reference": str(usuario.id),
        "sort": "date_created",
        "criteria": "desc"
    })

    for pago in search_result["response"]["results"]:
        if pago["status"] == "approved":
            print("✅ Pago detectado. Redirigiendo a success.")
            return redirect('success')  # 👈 acá lo llevás igual que si lo hubieran redirigido

    # Si no hay pago aprobado
    return redirect('inicio')  # o a donde quieras

class CrearTurnoView(View):
    template_name = 'miapp/crear_turno.html'

    def get(self, request, *args, **kwargs):
        form = TurnoForm()
        fecha_hora_form = TurnoFechaHoraForm()
        usuario = request.user
        miCarrito = Carrito.objects.filter(usuario=usuario).select_related('producto')
        total_duracion = sum(item.producto.duracion * item.cantidad for item in miCarrito)

        context = {
            'form': form,
            'fecha_hora_form': fecha_hora_form,
            'miCarrito': miCarrito,
            'total_duracion': total_duracion,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        accion = request.POST.get('accion')
        metodo_pago = request.POST.get('metodo_pago')

        if accion == "pagar_local":
            usuario = request.user
            miCarrito = Carrito.objects.filter(usuario=usuario).select_related('producto')
            return self.procesar_pago_local(request, miCarrito, usuario)

        form = TurnoDurationForm(request.POST)
        fecha_hora_form = TurnoFechaHoraForm(request.POST)

        if form.is_valid() and fecha_hora_form.is_valid():
            usuario = request.user
            duracion = form.cleaned_data['duracion']
            fecha_hora = fecha_hora_form.cleaned_data['fecha_hora']

            if is_naive(fecha_hora):
                fecha_hora = make_aware(fecha_hora)

            miCarrito = Carrito.objects.filter(usuario=usuario).select_related('producto')
            if not miCarrito.exists():
                return self.render_form(form, fecha_hora_form, 'No tienes productos en el carrito para crear un turno.')

            total_duracion = sum(item.producto.duracion * item.cantidad for item in miCarrito)
            if duracion != total_duracion:
                return self.render_form(form, fecha_hora_form, 'La duración total no coincide con los productos en el carrito.')

            fecha_hora_inicio = fecha_hora.replace(minute=0, second=0, microsecond=0)
            fecha_hora_fin = fecha_hora_inicio + timedelta(minutes=duracion)

            horario_apertura = 9
            horario_cierre = 19

            if fecha_hora_inicio.hour < horario_apertura or (fecha_hora_fin.hour >= horario_cierre and fecha_hora_fin.minute > 0):
                return self.render_form(form, fecha_hora_form, f'El horario de atención es de {horario_apertura}:00 a {horario_cierre}:00.')

            turnos_solapados = Turno.objects.filter(
                fecha_hora__lt=fecha_hora_fin,
                fecha_hora__gte=fecha_hora_inicio
            )

            if turnos_solapados.exists():
                return self.manejar_solapamiento(request, form, fecha_hora_form, turnos_solapados)

            # GUARDAMOS los datos en sesión para usarlos en la vista de pago
            print("Datos validos. Preparando para redirigir a iniciar_pago.")
            request.session['turno_data'] = {
                'usuario_id': usuario.id,
                'fecha_hora_inicio': fecha_hora_inicio.isoformat(),
                'duracion': duracion,
            }
            return redirect(reverse('iniciar_pago'))

        

        else:
            print("TurnoDurationForm errors:", form.errors)
            print("TurnoFechaHoraForm errors:", fecha_hora_form.errors)
            return self.render_form(form, fecha_hora_form, 'Error en los datos del formulario.')
        
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

class SuccessView(View):
    def get(self, request):
        usuario = request.user
        miCarrito = Carrito.objects.filter(usuario=usuario).select_related('producto')
        turno_data = request.session.pop('turno_data', None)

        if not turno_data or not miCarrito.exists():
            messages.error(request, 'No se pudo confirmar el turno.')
            return redirect('crear_turno')

        fecha_hora_str = turno_data.get('fecha_hora')
        if not fecha_hora_str:
            messages.error(request, 'No se encontró la fecha y hora del turno.')
            return redirect('crear_turno')

        fecha_hora_inicio = datetime.fromisoformat(fecha_hora_str)
        if fecha_hora_inicio.tzinfo is not None:
            fecha_hora_inicio = fecha_hora_inicio.astimezone(None).replace(tzinfo=None)

        duracion = turno_data.get('duracion', 0)
        turno = Turno.objects.create(cliente=usuario, duracion=duracion, fecha_hora=fecha_hora_inicio)

        for item in miCarrito:
            turno.productos.add(item.producto)
            item.delete()

        messages.success(request, '¡Turno confirmado!')
        return render(request, 'miapp/success.html', {'message': '¡Turno confirmado!'})


class FailureView(View):
    def get(self, request):
        return render(request, 'miapp/failure.html', {'error_message': "El pago ha fallado. Por favor, intenta nuevamente."})

class PendingView(View):
    def get(self, request):
        return render(request, 'miapp/pending.html', {'message': "Tu pago está pendiente. Te notificaremos una vez que se confirme."})



class TurnoConfirmadoPagoLocal(TemplateView):
    template_name = 'miapp/turno_confirmado.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el turno, por ejemplo, usando el id pasado como parámetro
        turno_id = self.request.GET.get('turno_id')  # Asegúrate de pasar el ID del turno en la URL
        if turno_id:
            turno = Turno.objects.get(id=turno_id)
            context['turno'] = turno  # Pasa el objeto turno al template

        return context


from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class CalendarioGuardarTurnoView(View):
    template_name = 'miapp/guardarturno.html'

    def get(self, request, *args, **kwargs):
        usuario = request.user
        productos_en_carrito = Carrito.objects.filter(usuario=usuario).select_related('producto')
        cantidad_en_carrito = Carrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0

        context = {
            'cantidad_en_carrito': cantidad_en_carrito,
            'productos_en_carrito': productos_en_carrito,
            'turnos_solapados': None,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        selected_services_ids = request.POST.get('selectedServices', '').split(',')
        fecha_hora_str = request.POST.get('fecha_hora')
        metodo_pago = request.POST.get('metodo_pago')
        usuario = request.user
        


        
        if not Carrito.objects.filter(usuario=usuario).exists():
            return JsonResponse({"status": "error", "message": "El carrito está vacío."})

        # 🔍 Validar antes de continuar
        validacion = validar_turno(selected_services_ids, fecha_hora_str)
        if validacion['status'] == 'error':
            return JsonResponse({
                'status': 'error',
                'message': validacion['message'],
                'turnos_solapados': validacion.get('turnos_solapados', [])
            })

        if metodo_pago == 'mercado_pago':
            # Si todo está validado, redirigimos a iniciar_pago
            request.session['fecha_hora'] = fecha_hora_str
            return JsonResponse({
                'status': 'redirect',
                'url': reverse('iniciar_pago')
            })

        elif metodo_pago == 'pago_local':
            try:
                print(f"🔍 Creando turno para usuario: {usuario}")
                print(f"🔍 Servicios: {selected_services_ids}")
                print(f"🔍 Fecha: {fecha_hora_str}")
                
                crear_turno(usuario, selected_services_ids, fecha_hora_str)
                
                print("✅ Turno creado exitosamente")
                return JsonResponse({
                    'status': 'success',  # ✅ JavaScript busca este status
                    'redirect_url': reverse('turno_confirmado'),  # ✅ URL para redirigir
                    'message': 'Turno creado exitosamente'
                })
                
            except Exception as e:
                print(f"❌ Error al crear turno: {e}")
                import traceback
                traceback.print_exc()
                
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error al crear el turno: {str(e)}'
                })

        else:
            return JsonResponse({"status": "error", "message": "Método de pago no válido."})



@method_decorator(csrf_exempt, name='dispatch')
class GuardarTurnoSesionView(View):
    def post(self, request):
        selected_services_ids = request.POST.get('selectedServices', '').split(',')
        fecha_hora_str = request.POST.get('fecha_hora')

        if not selected_services_ids or not fecha_hora_str:
            return JsonResponse({"status": "error", "message": "Datos incompletos."})

        total_duracion = Producto.objects.filter(id__in=selected_services_ids).aggregate(
            total=Sum('duracion'))['total'] or 0

        request.session['turno_data'] = {
            'servicios': selected_services_ids,
            'fecha_hora': fecha_hora_str,
            'usuario_id': request.user.id,
            'duracion': total_duracion,
        }
        return JsonResponse({"status": "success"})

    

@method_decorator(csrf_exempt, name='dispatch')
class PagoMercadoPagoModalView(View):
    def post(self, request):
        selected_services_ids = request.POST.get('selectedServices', '').split(',')
        fecha_hora_str = request.POST.get('fecha_hora')
        usuario = request.user
        User = get_user_model()

        if not selected_services_ids or not fecha_hora_str:
            return JsonResponse({"status": "error", "message": "Datos incompletos."})

        servicios = Producto.objects.filter(id__in=selected_services_ids)
        if not servicios.exists():
            return JsonResponse({"status": "error", "message": "Servicios no válidos."})

        # Calcular duración total
        total_duracion = sum(p.duracion for p in servicios)
        fecha_hora = make_aware(datetime.strptime(fecha_hora_str, "%Y-%m-%dT%H:%M"))

        # Guardar en sesión para confirmar post pago
        request.session['event_data'] = {
            'usuario': usuario.id,
            'servicios': selected_services_ids,
            'fecha_hora': fecha_hora_str,
            'total_duracion': total_duracion
        }

        # Crear preferencia en Mercado Pago
        mp = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

        items = [{
            "title": p.nombre,
            "quantity": 1,
            "unit_price": float(p.precio),
            "currency_id": "ARS"
        } for p in servicios]

        scheme = 'https' if not settings.DEBUG else 'http'
        host = request.get_host()

        preference_data = {
            "items": items,
            "payer": {
                "email": usuario.email
            },
            "back_urls": {
                "success": f"{scheme}://{host}{reverse('success')}",
                "failure": f"{scheme}://{host}{reverse('failure')}",
                "pending": f"{scheme}://{host}{reverse('pending')}",
            },
            "auto_return": "approved"
        }

        preference_response = mp.preference().create(preference_data)

        if preference_response["status"] != 201:
            return JsonResponse({"status": "error", "message": "Error al generar preferencia."})

        init_point = preference_response["response"]["init_point"]
        return JsonResponse({"status": "success", "url": init_point})



from django.http import JsonResponse
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from .models import Producto, Turno, Carrito

def crear_turno(usuario, selected_services_ids, fecha_hora_str):
    # Filtrar los IDs vacíos o no numéricos
    selected_services_ids = [id.strip() for id in selected_services_ids if id.strip().isdigit()]

    fecha_hora = make_aware(datetime.strptime(fecha_hora_str, "%Y-%m-%dT%H:%M"))
    servicios = Producto.objects.filter(id__in=selected_services_ids)

    total_duracion = sum(servicio.duracion for servicio in servicios)
    fecha_hora_inicio = fecha_hora.replace(minute=0, second=0, microsecond=0)
    fecha_hora_fin = fecha_hora_inicio + timedelta(minutes=total_duracion)

    # Validación del horario
    horario_apertura = 9
    horario_cierre = 19
    if fecha_hora_inicio.hour < horario_apertura or (fecha_hora_fin.hour >= horario_cierre and fecha_hora_fin.minute > 0):
        return JsonResponse({
            'status': 'error',
            'message': f'El horario de atención es de {horario_apertura}:00 a {horario_cierre}:00.',
            'turnos_solapados': []
        })

    # Validar solapamiento de turnos
    turnos_solapados = Turno.objects.filter(
        fecha_hora__lt=fecha_hora_fin,
        fecha_hora__gte=fecha_hora_inicio
    )

    if turnos_solapados.exists():
        turnos_solapados_list = list(turnos_solapados.values('fecha_hora', 'duracion'))
        return JsonResponse({
            'status': 'error',
            'message': 'El horario seleccionado está ocupado.',
            'turnos_solapados': turnos_solapados_list
        })

    # Crear el turno
    turno = Turno.objects.create(cliente=usuario, duracion=total_duracion, fecha_hora=fecha_hora)
    turno.productos.set(servicios)
    turno.save()

    # Vaciar el carrito del usuario
    Carrito.objects.filter(usuario=usuario).delete()
    irAConfirmacion()
    # Retornar el JSON con el mensaje y la URL de redirección
    return JsonResponse({
        'status': 'success',
        'message': 'Evento guardado, espera a confirmar el pago para crear el turno.',
        'redirect_url': 'confirmacion_turno/'  # Asegúrate de que esta URL exista en `urls.py`
    })

def validar_turno(selected_services_ids, fecha_hora_str):
    selected_services_ids = [id.strip() for id in selected_services_ids if id.strip().isdigit()]
    try:
        fecha_hora = make_aware(datetime.strptime(fecha_hora_str, "%Y-%m-%dT%H:%M"))
    except ValueError:
        return {'status': 'error', 'message': 'Formato de fecha inválido.', 'turnos_solapados': []}

    servicios = Producto.objects.filter(id__in=selected_services_ids)
    total_duracion = sum(servicio.duracion for servicio in servicios)

    fecha_hora_inicio = fecha_hora.replace(minute=0, second=0, microsecond=0)
    fecha_hora_fin = fecha_hora_inicio + timedelta(minutes=total_duracion)

    if fecha_hora_inicio.hour < 9 or (fecha_hora_fin.hour >= 19 and fecha_hora_fin.minute > 0):
        return {
            'status': 'error',
            'message': 'El horario de atención es de 9:00 a 19:00.',
            'turnos_solapados': []
        }

    turnos_solapados = Turno.objects.filter(
        fecha_hora__lt=fecha_hora_fin,
        fecha_hora__gte=fecha_hora_inicio
    )

    if turnos_solapados.exists():
        return {
            'status': 'error',
            'message': 'Ya existe un turno en ese horario. Por favor, elegí otro.',
            'turnos_solapados': list(turnos_solapados.values('fecha_hora', 'duracion'))
        }

    return {'status': 'ok', 'total_duracion': total_duracion}




def irAConfirmacion():
    return redirect('success')




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
        return redirect('guardar_turno')

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
        return redirect('guardar_turno')
        
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

class QuienesSomosView(TemplateView):
    template_name = 'miapp/quienessomos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            cantidad = Carrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        else:
            cantidad = 0

        context['cantidad_en_carrito'] = cantidad
        return context