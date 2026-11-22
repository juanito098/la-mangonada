from django.db import models
from django.contrib.auth.models import User

# Tu modelo original de empleado
class empleado(models.Model):
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    correo = models.EmailField(blank=True, null=True)

    def _str_(self):
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

    def _str_(self):
        return f"Pedido de {self.nombre_cliente} - Total: ${self.total}"