

from django.urls import path, include
from .views import *
from . import views


from django.contrib.auth.views import LogoutView


urlpatterns = [
   path('inicio/', views.inicio, name='inicio'),
   path('guardarturno/', CalendarioGuardarTurnoView.as_view(), name='guardar_turno'),
   path('perfil_usuario/', views.perfil_usuario, name='perfil_usuario'),
   path('base_ventas/', views.base_ventas, name='base_ventas'),
   path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
   path('cambiar_clave/', views.cambiar_clave, name='cambiar_clave'),
   path('editar_articulo/<int:id>/', views.editar_articulo, name='editar_articulo'),
   path('lista_articulos/', views.lista_articulos, name='lista_articulos'),# lista_articulos
       #URLS DE LAS FALLAS DEL MERCADO PAGO
    path('failure/', FailureView.as_view(), name='failure'),
    path('pending/', PendingView.as_view(), name='pending'),
    path('success/', SuccessView.as_view(), name='success'),
    path('turno_confirmado/', TurnoConfirmadoPagoLocal.as_view(), name='turno_confirmado'),

    



   
   path('registro_exitoso/', RegistroExitoso.as_view(), name='registro_exitoso'),

   path('home/',HomreView.as_view(),name="home"),
   path('',HomeViewVentas.as_view(),name="home_ventas"),
   path('search_results/', ProductSearchView.as_view(), name='search_results'),
   path('login/', MyLoginView.as_view(), name='login'),
   path('logout/', LogoutView.as_view(next_page='home_ventas'), name='logout'),
   path('confirmar_turno/', ConfirmarTurnoView.as_view(), name='confirmar_turno'),
   path('agregar-al-carrito/', AgregarAlCarritoView.as_view(), name='agregar_al_carrito'),
   path('crear-turno/', CrearTurnoView.as_view(), name='crear_turno'),
   path('eliminar/<int:item_id>/', EliminarDelCarritoView.as_view(), name='eliminar'),
   path('aumentar/<int:item_id>/', AumentarCantidadView.as_view(), name='aumentar'),
   path('disminuir/<int:item_id>/', DisminuirCantidadView.as_view(), name='disminuir'),
   path('agenda/', AgendaView.as_view(), name='agenda'),
   path('calendar/', CalendarView.as_view(), name='calendar'),
   path('calendario_turnos/', VerCalendarioTurnosView.as_view(), name='calendario_turnos'),




   path('no_registrado/', NoRegistradoView.as_view(), name='no_registrado'),
   path('registro/', RegistroUsuario.as_view(), name="registro"),
   path('turno/<int:pk>/', TurnoDetailView.as_view(), name='turno_detail'),
   path('turno_detail_cliente/<int:pk>/', TurnoDetailClienteView.as_view(), name='turno_detail_cliente'),
   path('payment/', PaymentView.as_view(), name='payment'),
   path('success/', PaymentSuccessView.as_view(), name='success'),
   path('confirmacion_turno/', ConfirmacionTurnoView.as_view(), name='confirmacion_turno'),
   path('restricted/', RestrictedPageView.as_view(), name='restricted'),
   path('crear_categoria/', CategoriaCreateView.as_view(), name='crear_categoria'),
   path('categoria/', CategoriaListView.as_view(), name="categoria"),
   path('producto/<int:pk>/', ProductoDetailView.as_view(), name='producto_detail'),
   path('peluqueria/', PeluqueriaListView.as_view(), name='peluqueria'),
   path('manicuria/', ManicuriaListView.as_view(), name='manicuria'),
 
    
   
   
   
   
    path('producto/',ProductoList.as_view(),name="producto"),
    path('cliente/',ClienteList.as_view(),name="cliente"),
    path('turno/',TurnoList.as_view(),name="turno"),
   
    # AMB productos
    path('producto_create/',ProductoCreate.as_view(),name="producto_create"),
    path('producto_update/<int:pk>/', ProductoUpdate.as_view(), name="producto_update"),
    path('producto_delete/<int:pk>/',  ProductoDelete.as_view(), name="producto_delete"),
    
    # ABM Clientes
    path('cliente_create/',ClienteCreate.as_view(),name="cliente_create"),
    path('cliente_update/<int:pk>/', ClienteUpdate.as_view(), name="cliente_update"),
    path('cliente_delete/<int:pk>/',  ClienteDelete.as_view(), name="cliente_delete"),

    # ABM Turnos
    path('turno_create/',TurnoCreate.as_view(),name="turno_create"),
    path('turno_update/<int:pk>/', TurnoUpdate.as_view(), name="turno_update"),
    path('turno_delete/<int:pk>/',  TurnoDelete.as_view(), name="turno_delete"),

    
    path('ver_mis_turnos',  VerMisTurnosView.as_view(), name="ver_mis_turnos"),
    
    
    path('crear_articulo/', views.crear_articulo, name='crear_articulo'),
    path('iniciar-pago/', IniciarPagoView.as_view(), name='iniciar_pago'),#ventana de boton de mercado pago
    path('iniciar-pago-modal/', PagoMercadoPagoModalView.as_view(), name='iniciar_pago_modal'),#modal que me lleva a iniciar pago (NO modificar)

    
    path('guardar-turno-sesion/', GuardarTurnoSesionView.as_view(), name='guardar_turno_sesion'),
    path('quienessomos/', QuienesSomosView.as_view(),name='quienessomos'),
    
]


