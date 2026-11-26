from django.db import models
from django.contrib.auth.models import User

# Tu modelo de empleado / postulantes
class empleado(models.Model):
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    correo = models.EmailField(blank=True, null=True)
    en_nosotros = models.BooleanField(default=True)

    def str(self):
        return self.nombre

# Modelo completo para el checkout del carrito
class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre_cliente = models.CharField(max_length=150, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)
    metodo_pago = models.CharField(max_length=50, null=True, blank=True)
    productos_detalle = models.TextField()
    total = models.DecimalField(max_digits=8, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Pedido de {self.nombre_cliente} - Total: ${self.total}"

# Modelo para productos agregados desde el panel del superusuario
class Producto(models.Model):
    CATEGORIAS = [
        ('mangonada', 'Mangonada'),
        ('boyo', 'Boyo Cremosito'),
    ]

    nombre = models.CharField(max_length=120)
    descripcion = models.CharField(max_length=255, blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=15.00)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='boyo')
    imagen = models.ImageField(upload_to='productos/')
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def _str_(self):
        return f"{self.nombre} (${self.precio})"
