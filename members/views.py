import json
import re
from urllib.parse import quote
import cloudinary.uploader
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Pedido, Producto, empleado


TELEFONO_TIENDA = '5218311836953'  # <-- Pon aquí tu número de WhatsApp con código de país
CORREO_TIENDA = 'castleclashyeti@gmail.com'


def limpiar_telefono(telefono, codigo_pais='52'):
    digitos = re.sub(r'\D', '', str(telefono or ''))
    if len(digitos) == 10 and codigo_pais:
        digitos = f'{codigo_pais}{digitos}'
    return digitos


def construir_enlaces_whatsapp(telefono_tienda, telefono_cliente, resumen_pedido):
    tel_tienda = limpiar_telefono(telefono_tienda)
    tel_cliente = limpiar_telefono(telefono_cliente)

    mensaje_tienda = f'Nuevo pedido confirmado - La Mangonada:\n{resumen_pedido}'
    mensaje_cliente = (
        f'¡Gracias por tu compra en La Mangonada! Aquí tienes tu confirmación:\n{resumen_pedido}'
    )

    url_tienda = (
        f'https://wa.me/{tel_tienda}?text={quote(mensaje_tienda)}'
        if tel_tienda
        else ''
    )
    url_cliente = (
        f'https://wa.me/{tel_cliente}?text={quote(mensaje_cliente)}'
        if tel_cliente
        else ''
    )

    return url_tienda, url_cliente


def enviar_confirmacion_correo(asunto, cuerpo, correo_usuario=None):
    try:
        destinatarios = [CORREO_TIENDA]
        if correo_usuario and correo_usuario.strip():
            correo_limpio = correo_usuario.strip()
            if correo_limpio not in destinatarios:
                destinatarios.append(correo_limpio)

        send_mail(
            asunto,
            cuerpo,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost'),
            destinatarios,
            fail_silently=True,
        )
    except Exception:
        pass


def es_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


def es_superusuario(user):
    return user.is_authenticated and user.is_superuser


def index(request):
    return render(request, 'index.html')


def contactos(request):
    if request.method == 'POST':
        nombre_ingresado = request.POST.get('nombre')
        edad_ingresada = request.POST.get('edad')
        correo_ingresado = request.POST.get('correo')

        if nombre_ingresado and edad_ingresada:
            empleado.objects.create(
                nombre=nombre_ingresado,
                edad=edad_ingresada,
                correo=correo_ingresado,
                en_nosotros=False,
            )
            messages.success(request, '¡Tu postulación fue enviada con éxito!')
            return redirect('contactos')

    admin_activo = es_admin(request.user)
    candidatos = empleado.objects.all() if admin_activo else None
    return render(
        request,
        'contactos.html',
        {
            'candidatos': candidatos,
            'es_admin': admin_activo,
        },
    )


@login_required(login_url='login')
@user_passes_test(es_admin, login_url='login')
def eliminar_candidato(request, id):
    candidato = get_object_or_404(empleado, id=id)
    candidato.delete()
    return redirect('contactos')


@login_required(login_url='login')
@user_passes_test(es_admin, login_url='login')
def editar_candidato(request, id):
    candidato = get_object_or_404(empleado, id=id)
    if request.method == 'POST':
        candidato.nombre = request.POST.get('nombre')
        candidato.edad = request.POST.get('edad')
        candidato.correo = request.POST.get('correo')
        candidato.save()
        return redirect('contactos')

    return render(request, 'editar_candidato.html', {'candidato': candidato})


# ==========================================
# VISTAS DE PRODUCTOS Y PEDIDOS (CRUD ADMIN)
# ==========================================
def productos(request):
    admin_activo = es_admin(request.user)
    superusuario_activo = es_superusuario(request.user)
    pedidos = Pedido.objects.all().order_by('-id') if admin_activo else None
    mangonadas_db = Producto.objects.filter(activo=True, categoria='mangonada')
    boyos_db = Producto.objects.filter(activo=True, categoria='boyo')
    return render(
        request,
        'productos.html',
        {
            'pedidos': pedidos,
            'es_admin': admin_activo,
            'es_superusuario': superusuario_activo,
            'mangonadas_db': mangonadas_db,
            'boyos_db': boyos_db,
        },
    )


@login_required(login_url='login')
@user_passes_test(es_superusuario, login_url='productos')
def agregar_producto(request):
    if request.method == 'POST':
        nombre = (request.POST.get('nombre') or '').strip()
        descripcion = (request.POST.get('descripcion') or '').strip()
        categoria = (request.POST.get('categoria') or 'boyo').strip()
        precio_raw = (request.POST.get('precio') or '15').strip()
        imagen = request.FILES.get('imagen')

        if categoria not in ('mangonada', 'boyo'):
            categoria = 'boyo'

        try:
            precio_val = float(precio_raw)
        except ValueError:
            precio_val = 0

        if not nombre:
            messages.error(request, 'Escribe el nombre del producto.')
            return redirect('productos')

        if precio_val <= 0:
            messages.error(request, 'El precio debe ser mayor a 0.')
            return redirect('productos')

        if not imagen:
            messages.error(request, 'Selecciona una imagen para el producto.')
            return redirect('productos')

        try:
            resultado = cloudinary.uploader.upload(
                imagen, folder='la_mangonada/productos'
            )
            url_imagen = resultado.get('secure_url', '')
        except Exception as e:
            messages.error(request, f'Error Cloudinary: {e}')
            return redirect('productos')

        try:
            Producto.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio_val,
                categoria=categoria,
                imagen_url=url_imagen,
                activo=True,
            )
            messages.success(request, f'Producto "{nombre}" agregado con éxito.')
        except Exception as e:
            messages.error(request, f'Error al guardar en BD: {e}')

    return redirect('productos')


@login_required(login_url='login')
@user_passes_test(es_superusuario, login_url='productos')
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        nombre = (request.POST.get('nombre') or '').strip()
        descripcion = (request.POST.get('descripcion') or '').strip()
        categoria = (request.POST.get('categoria') or producto.categoria).strip()
        precio_raw = (request.POST.get('precio') or str(producto.precio)).strip()
        imagen = request.FILES.get('imagen')

        if categoria not in ('mangonada', 'boyo'):
            categoria = producto.categoria

        try:
            precio_val = float(precio_raw)
        except ValueError:
            precio_val = float(producto.precio)

        if nombre:
            producto.nombre = nombre
        producto.descripcion = descripcion
        producto.categoria = categoria
        if precio_val > 0:
            producto.precio = precio_val

        if imagen:
            try:
                resultado = cloudinary.uploader.upload(
                    imagen, folder='la_mangonada/productos'
                )
                producto.imagen_url = resultado.get('secure_url', producto.imagen_url)
            except Exception as e:
                messages.error(request, f'Error al subir la nueva imagen: {e}')
                return redirect('editar_producto', id=producto.id)

        producto.save()
        messages.success(request, f'Producto "{producto.nombre}" actualizado.')
        return redirect('productos')

    return render(
        request,
        'editar_producto.html',
        {
            'producto': producto,
            'es_admin': es_admin(request.user),
            'es_superusuario': es_superusuario(request.user),
        },
    )


@login_required(login_url='login')
@user_passes_test(es_superusuario, login_url='productos')
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado.')
    return redirect('productos')


@login_required(login_url='login')
@user_passes_test(es_admin, login_url='login')
def eliminar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    pedido.delete()
    return redirect('productos')


@login_required(login_url='login')
@user_passes_test(es_admin, login_url='login')
def editar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    if request.method == 'POST':
        pedido.nombre_cliente = request.POST.get('nombre_cliente')
        pedido.telefono = request.POST.get('telefono')
        pedido.direccion = request.POST.get('direccion')
        pedido.metodo_pago = request.POST.get('metodo_pago')
        pedido.productos_detalle = request.POST.get('productos_detalle')
        pedido.total = float(request.POST.get('total', 0))
        pedido.save()
        return redirect('productos')

    return render(request, 'editar_pedido.html', {'pedido': pedido})


def servicios(request):
    return render(request, 'servicios.html')


def nosotros(request):
    mis_empleados = empleado.objects.filter(en_nosotros=True)
    contexto = {
        'empleados': mis_empleados,
    }
    return render(request, 'nosotros.html', contexto)


# ==========================================
# SECCIÓN DE USUARIOS REGISTRADOS (SOLO ADMIN)
# ==========================================
@login_required(login_url='login')
@user_passes_test(es_admin, login_url='login')
def lista_usuarios(request):
    usuarios = User.objects.all().order_by('-date_joined')
    return render(request, 'usuarios.html', {'usuarios': usuarios, 'es_admin': True})


@login_required(login_url='login')
@user_passes_test(es_admin, login_url='login')
def eliminar_usuario(request, id):
    usuario_objetivo = get_object_or_404(User, id=id)
    if usuario_objetivo != request.user:
        usuario_objetivo.delete()
    return redirect('lista_usuarios')


# ==========================================
# VISTAS DE INICIO DE SESIÓN Y REGISTRO
# ==========================================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            enviar_confirmacion_correo(
                asunto='Confirmación de inicio de sesión - La Mangonada',
                cuerpo=(
                    f'Hola {user.username}, se registró un inicio de sesión en tu cuenta de La Mangonada.\n'
                    f'Correo registrado: {user.email or "No especificado"}'
                ),
                correo_usuario=user.email,
            )

            messages.success(
                request,
                'Sesión iniciada. Se envió la confirmación al correo registrado (si aplica).',
            )
            next_url = request.GET.get('next') or 'index'
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'login.html')


def registro_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not username or not password:
            messages.error(request, 'Completa usuario y contraseña.')
        elif password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ese nombre de usuario ya está en uso.')
        else:
            nuevo_usuario = User.objects.create_user(
                username=username, email=email, password=password
            )
            login(request, nuevo_usuario)

            enviar_confirmacion_correo(
                asunto='Confirmación de creación de cuenta - La Mangonada',
                cuerpo=(
                    f'¡Bienvenido a La Mangonada, {nuevo_usuario.username}!\n'
                    f'Tu cuenta fue creada correctamente.\n'
                    f'Correo: {email or "No especificado"}'
                ),
                correo_usuario=email,
            )

            messages.success(
                request,
                'Cuenta creada con éxito. Se envió el mensaje de confirmación al correo.',
            )
            return redirect('index')

    return render(request, 'registro.html')


def logout_view(request):
    logout(request)
    return redirect('index')


# ==========================================
# FUNCIÓN PARA GUARDAR EL CARRITO (POST)
# ==========================================
def guardar_pedido(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    'status': 'auth_required',
                    'message': 'Debes iniciar sesión o registrarte antes para comprar.'
                },
                status=401,
            )

        try:
            data = json.loads(request.body)
            nombre_cliente = data.get('nombre_cliente', '')
            telefono = data.get('telefono', '')
            direccion = data.get('direccion', '')
            metodo_pago = data.get('metodo_pago', 'Efectivo')
            productos_lista = data.get('productos', [])
            total_str = str(data.get('total', '$0.00')).replace('$', '').replace(',', '').strip()

            detalle_texto = ', '.join(
                [f"{p['nombre']} (x{p['cantidad']})" for p in productos_lista]
            )
            total_num = float(total_str)

            pedido = Pedido.objects.create(
                usuario=request.user,
                nombre_cliente=nombre_cliente,
                telefono=telefono,
                direccion=direccion,
                metodo_pago=metodo_pago,
                productos_detalle=detalle_texto,
                total=total_num,
            )

            resumen_pedido = (
                f'Pedido #{pedido.id}\n'
                f'Cliente: {nombre_cliente}\n'
                f'Teléfono: {telefono}\n'
                f'Dirección: {direccion}\n'
                f'Método de pago: {metodo_pago}\n'
                f'Productos: {detalle_texto}\n'
                f'Total: ${total_num:.2f}'
            )

            url_wa_tienda, url_wa_cliente = construir_enlaces_whatsapp(
                TELEFONO_TIENDA,
                telefono,
                resumen_pedido,
            )

            enviar_confirmacion_correo(
                asunto=f'Confirmación de compra #{pedido.id} - La Mangonada',
                cuerpo=(
                    f'¡Hola! Se ha confirmado una compra en La Mangonada.\n\n'
                    f'{resumen_pedido}\n'
                ),
                correo_usuario=request.user.email,
            )

            return JsonResponse(
                {
                    'status': 'success',
                    'message': '¡Pedido registrado con éxito! Se envió confirmación al correo y puedes confirmar por WhatsApp.',
                    'pedido_id': pedido.id,
                    'url_wa_tienda': url_wa_tienda,
                    'url_wa_cliente': url_wa_cliente,
                }
            )
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
