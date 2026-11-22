from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index),
    path('contactos.html', views.contactos, name='contactos'),
    path('contactos/eliminar/<int:id>/', views.eliminar_candidato, name='eliminar_candidato'),
    path('contactos/editar/<int:id>/', views.editar_candidato, name='editar_candidato'),
    path('productos.html', views.productos, name='productos'),
    path('servicios.html', views.servicios, name='servicios'),
    path('nosotros.html', views.nosotros, name='nosotros'),
    path('guardar_pedido/', views.guardar_pedido, name='guardar_pedido'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('eliminar_pedido/<int:id>/', views.eliminar_pedido, name='eliminar_pedido'),
    path('editar_pedido/<int:id>/', views.editar_pedido, name='editar_pedido'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('eliminar_usuario/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
]