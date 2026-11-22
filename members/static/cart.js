var carrito = [];

var OPCIONES_MANGONADA = ['Taj\u00edn', 'Lim\u00f3n', 'Chamoy', 'Ticko dulce'];

function obtenerExtrasMangonada() {
    var checks = document.querySelectorAll('.chip-checkbox:checked');
    var seleccionados = [];

    for (var i = 0; i < checks.length; i++) {
        var valor = checks[i].value;
        if (OPCIONES_MANGONADA.indexOf(valor) !== -1) {
            seleccionados.push(valor);
        }
    }

    return seleccionados;
}

function limpiarChipsMangonada() {
    var checks = document.querySelectorAll('.chip-checkbox');
    for (var i = 0; i < checks.length; i++) {
        checks[i].checked = false;
    }
}

function agregarAlCarrito(nombre, precio, tipo) {
    if (!tipo) {
        tipo = 'boyo';
    }

    var esMangonada = (tipo === 'mangonada');
    var extras = esMangonada ? obtenerExtrasMangonada() : [];
    var textoExtras = esMangonada ? extras.join(', ') : '';

    if (esMangonada) {
        limpiarChipsMangonada();
    }

    var claveUnica = esMangonada
        ? ('mangonada_' + nombre + '_' + textoExtras)
        : ('boyo__' + nombre);

    var productoExistente = null;
    for (var i = 0; i < carrito.length; i++) {
        if (carrito[i].claveUnica === claveUnica) {
            productoExistente = carrito[i];
            break;
        }
    }

    if (productoExistente) {
        productoExistente.cantidad += 1;
    } else {
        var nombreFinal = (esMangonada && extras.length > 0)
            ? (nombre + ' (' + textoExtras + ')')
            : nombre;

        carrito.push({
            claveUnica: claveUnica,
            tipo: tipo,
            nombreBase: nombre,
            extras: extras,
            nombre: nombreFinal,
            precio: precio,
            cantidad: 1
        });
    }

    actualizarCarritoVisual();
}

function cambiarCantidad(claveUnica, cambio) {
    for (var i = 0; i < carrito.length; i++) {
        if (carrito[i].claveUnica === claveUnica) {
            carrito[i].cantidad += cambio;
            if (carrito[i].cantidad <= 0) {
                carrito.splice(i, 1);
            }
            break;
        }
    }
    actualizarCarritoVisual();
}

function actualizarCarritoVisual() {
    var listaCarrito = document.getElementById('lista-carrito');
    var totalCarrito = document.getElementById('total-carrito');

    if (!listaCarrito) {
        return;
    }

    listaCarrito.innerHTML = '';

    if (carrito.length === 0) {
        listaCarrito.innerHTML = '<p class="carrito-vacio">Tu carrito est\u00e1 vac\u00edo.</p>';
        if (totalCarrito) {
            totalCarrito.innerText = '$0.00';
        }
        return;
    }

    var total = 0;

    for (var i = 0; i < carrito.length; i++) {
        var item = carrito[i];
        var subtotal = item.precio * item.cantidad;
        total += subtotal;

        var divItem = document.createElement('div');
        divItem.className = 'item-carrito-visual';

        var lineaExtrasHtml = '';
        if (item.tipo === 'mangonada') {
            if (item.extras && item.extras.length > 0) {
                lineaExtrasHtml = '<div>Con extra: ' + item.extras.join(', ') + ' (seleccionada)</div>';
            } else {
                lineaExtrasHtml = '<div>Sin extra adicional (seleccionada)</div>';
            }
        }

        divItem.innerHTML =
            '<div>' +
                '<span>' + item.nombreBase + ' (x' + item.cantidad + ')</span>' +
                lineaExtrasHtml +
            '</div>' +
            '<div>' +
                '<span class="item-carrito-subtotal">$' + subtotal.toFixed(2) + '</span>' +
                '<button type="button" class="item-carrito-btn" onclick="cambiarCantidad(\'' + item.claveUnica + '\', 1)">+</button>' +
                '<button type="button" class="item-carrito-btn" onclick="cambiarCantidad(\'' + item.claveUnica + '\', -1)">-</button>' +
            '</div>';

        listaCarrito.appendChild(divItem);
    }

    if (totalCarrito) {
        totalCarrito.innerText = '$' + total.toFixed(2);
    }
}

function toggleCamposTarjeta() {
    var metodo = document.getElementById('metodo-pago').value;
    var contenedorTarjeta = document.getElementById('datos-tarjeta');
    if (!contenedorTarjeta) {
        return;
    }

    if (metodo === 'Tarjeta') {
        contenedorTarjeta.classList.remove('oculto');
    } else {
        contenedorTarjeta.classList.add('oculto');
    }
}

function mostrarAvisoSesion(mensaje) {
    var avisoExistente = document.getElementById('aviso-sesion-compra');
    if (avisoExistente) {
        avisoExistente.remove();
    }

    var contenedor = document.querySelector('.seccion-carrito') || document.body;
    var recuadro = document.createElement('div');
    recuadro.id = 'aviso-sesion-compra';
    recuadro.className = 'aviso-sesion-compra';

    var textoAviso = mensaje || 'Debes iniciar sesi\u00f3n o registrarte antes para comprar.';

    recuadro.innerHTML =
        '<div class="aviso-sesion-header">' +
            '<strong>' + textoAviso + '</strong>' +
            '<button type="button" class="aviso-sesion-cerrar" onclick="this.closest(\'#aviso-sesion-compra\').remove()">&times;</button>' +
        '</div>' +
        '<div class="aviso-sesion-acciones">' +
            '<a href="/login/" class="btn-aviso-login">Iniciar sesi\u00f3n</a>' +
            '<a href="/registro/" class="btn-aviso-registro">Registrarse</a>' +
        '</div>';

    contenedor.appendChild(recuadro);
}

function mostrarBotonesWhatsApp(data) {
    var panelExistente = document.getElementById('confirmacion-whatsapp-pedido');
    if (panelExistente) {
        panelExistente.remove();
    }

    var contenedor = document.querySelector('.seccion-carrito') || document.body;
    var panel = document.createElement('div');
    panel.id = 'confirmacion-whatsapp-pedido';
    panel.style.cssText = 'margin-top: 16px; padding: 14px; border: 1px solid #25D366; border-radius: 8px; background: #f4fff8;';

    var titulo = document.createElement('p');
    titulo.style.cssText = 'margin: 0 0 10px 0; font-weight: bold;';
    titulo.textContent = data.pedido_id
        ? ('Pedido #' + data.pedido_id + ' registrado. Confirmar por WhatsApp:')
        : 'Pedido registrado. Confirmar por WhatsApp:';
    panel.appendChild(titulo);

    var botonesContenedor = document.createElement('div');
    botonesContenedor.style.cssText = 'display: flex; gap: 10px; flex-wrap: wrap;';

    if (data.url_wa_cliente) {
        var btnCliente = document.createElement('a');
        btnCliente.href = data.url_wa_cliente;
        btnCliente.target = '_blank';
        btnCliente.rel = 'noopener noreferrer';
        btnCliente.textContent = 'Enviar confirmaci\u00f3n a mi WhatsApp';
        btnCliente.style.cssText = 'display: inline-block; padding: 10px 14px; background: #25D366; color: #fff; text-decoration: none; border-radius: 6px; font-weight: bold;';
        botonesContenedor.appendChild(btnCliente);
    }

    if (data.url_wa_tienda) {
        var btnTienda = document.createElement('a');
        btnTienda.href = data.url_wa_tienda;
        btnTienda.target = '_blank';
        btnTienda.rel = 'noopener noreferrer';
        btnTienda.textContent = 'Enviar copia a La Mangonada (Tienda)';
        btnTienda.style.cssText = 'display: inline-block; padding: 10px 14px; background: #128C7E; color: #fff; text-decoration: none; border-radius: 6px; font-weight: bold;';
        botonesContenedor.appendChild(btnTienda);
    }

    panel.appendChild(botonesContenedor);
    contenedor.appendChild(panel);
}

function enviarPedidoBackend() {
    var nombre = document.getElementById('nombre-cliente').value.trim();
    var telefono = document.getElementById('telefono-cliente').value.trim();
    var direccion = document.getElementById('direccion-cliente').value.trim();
    var metodoPago = document.getElementById('metodo-pago').value;

    if (!nombre || !telefono || !direccion) {
        alert('Por favor completa todos tus datos de env\u00edo (Nombre, Tel\u00e9fono y Direcci\u00f3n).');
        return;
    }

    if (carrito.length === 0) {
        alert('El carrito est\u00e1 vac\u00edo, agrega productos antes de comprar.');
        return;
    }

    var terminacionTarjeta = '';

    if (metodoPago === 'Tarjeta') {
        var numTarjeta = document.getElementById('numero-tarjeta').value.replace(/\s+/g, '');
        var mesTarjeta = document.getElementById('mes-tarjeta').value.trim();
        var cvvTarjeta = document.getElementById('cvv-tarjeta').value.trim();

        if (!/^\d{16}$/.test(numTarjeta)) {
            alert('Ingresa un n\u00famero de tarjeta v\u00e1lido de 16 d\u00edgitos.');
            return;
        }
        if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(mesTarjeta)) {
            alert('Ingresa la vigencia en formato MM/AA (ej. 08/28).');
            return;
        }
        if (!/^\d{3,4}$/.test(cvvTarjeta)) {
            alert('Ingresa un CVV v\u00e1lido de 3 o 4 d\u00edgitos.');
            return;
        }

        terminacionTarjeta = numTarjeta.slice(-4);
    }

    var datosPedido = {
        nombre_cliente: nombre,
        telefono: telefono,
        direccion: direccion,
        metodo_pago: metodoPago === 'Tarjeta' ? ('Tarjeta (** ' + terminacionTarjeta + ')') : metodoPago,
        productos: carrito,
        total: document.getElementById('total-carrito').innerText
    };

    var csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    var csrfToken = csrfInput ? csrfInput.value : '';

    fetch('/guardar_pedido/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(datosPedido)
    })
    .then(function(response) {
        return response.json().then(function(data) {
            return { status: response.status, data: data };
        });
    })
    .then(function(res) {
        var status = res.status;
        var data = res.data;

        if (status === 401 || data.status === 'auth_required') {
            mostrarAvisoSesion(data.message);
            return;
        }

        if (status >= 200 && status < 300 && data.status === 'success') {
            var avisoExistente = document.getElementById('aviso-sesion-compra');
            if (avisoExistente) {
                avisoExistente.remove();
            }

            alert('\u00a1Pedido realizado con \u00e9xito! Gracias por tu compra.');
            carrito = [];
            actualizarCarritoVisual();
            document.getElementById('nombre-cliente').value = '';
            document.getElementById('telefono-cliente').value = '';
            document.getElementById('direccion-cliente').value = '';
            document.getElementById('numero-tarjeta').value = '';
            document.getElementById('mes-tarjeta').value = '';
            document.getElementById('cvv-tarjeta').value = '';
            toggleCamposTarjeta();

            mostrarBotonesWhatsApp(data);
        } else {
            alert('Error al procesar: ' + (data.message || 'No se pudo completar el pedido.'));
        }
    })
    .catch(function(error) {
        console.error('Error:', error);
        alert('Ocurri\u00f3 un error de conexi\u00f3n con el servidor.');
    });
}