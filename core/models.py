from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    SYSTEM_ADMIN = 'SYSTEM_ADMIN'
    INTEGRAL = 'INTEGRAL'
    SATELITE = 'SATELITE'
    CLIENTE = 'CLIENTE'
    
    ROLE_CHOICES = [
        (CLIENTE, 'Cliente'),
        (INTEGRAL, 'Microempresa Integral'),
        (SATELITE, 'Microempresa Satélite'),
        (SYSTEM_ADMIN, 'Administrador del Sistema'),
    ]
    
    role = models.CharField(max_length=12, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    
    def is_integral(self):
        return self.role == 'INTEGRAL'
    
    def is_satelite(self):
        return self.role == 'SATELITE'
    
    def is_cliente(self):
        return self.role == self.CLIENTE
    
    def save(self, *args, **kwargs):
        if self.is_superuser and not self.role:
            self.role = self.SYSTEM_ADMIN
        super().save(*args, **kwargs)

    def is_system_admin(self):
        return self.role == self.SYSTEM_ADMIN or self.is_superuser

class MicroempresaIntegral(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100, default='Sin título')
    logo = models.ImageField(upload_to='empresas/logos/', blank=True, null=True)
    eslogan = models.CharField(max_length=200, blank=True, null=True)
    direccion = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.titulo

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.usuario.username

class MicroempresaSatelite(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100, default='Sin título')
    logo = models.ImageField(upload_to='empresas/logos/', blank=True, null=True)
    eslogan = models.CharField(max_length=200, blank=True, null=True)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20, blank=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.usuario.username

class Servicio(models.Model):
    TIPO_CHOICES = [
        ('CONFECCION', 'Confección'),
        ('ARREGLO', 'Arreglo'),
        ('OTRO', 'Otro'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='servicios/', blank=True, null=True)
    tipo_servicio = models.CharField(max_length=20, choices=TIPO_CHOICES)
    microempresa_satelite = models.ForeignKey(MicroempresaSatelite, on_delete=models.CASCADE, related_name='servicios')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Administrador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

class MateriaPrima(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()

class InventarioMateriaPrima(models.Model):
    microempresa_integral = models.ForeignKey(MicroempresaIntegral, on_delete=models.CASCADE)
    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    microempresa_integral = models.ForeignKey(MicroempresaIntegral, on_delete=models.CASCADE, related_name='productos', null=True, blank=True)
    stock = models.IntegerField(default=0)

class InventarioProductos(models.Model):
    microempresa_integral = models.ForeignKey(MicroempresaIntegral, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PRODUCCION', 'En Producción'),
        ('TERMINADO', 'Terminado'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado')
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    microempresa_integral = models.ForeignKey(MicroempresaIntegral, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.BooleanField(default=False)

class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

class PedidoPersonalizado(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('ACEPTADO', 'Aceptado'),
        ('RECHAZADO', 'Rechazado')
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    microempresa_integral = models.ForeignKey(MicroempresaIntegral, on_delete=models.CASCADE)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    precio_acordado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tiempo_entrega = models.IntegerField(null=True, blank=True, help_text='Días para entrega')
    razon_rechazo = models.TextField(null=True, blank=True)
    pagado = models.BooleanField(default=False)

class SolicitudConfeccion(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('COTIZADO', 'Cotizado'),
        ('PAGADO', 'Pagado')
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    microempresa_satelite = models.ForeignKey(MicroempresaSatelite, on_delete=models.CASCADE)
    descripcion = models.TextField()
    cantidad_prendas = models.IntegerField()
    tipo_prenda = models.CharField(max_length=100)
    cotizacion = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    pagado = models.BooleanField(default=False)

class TransaccionPago(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADO', 'Completado'),
        ('FALLIDO', 'Fallido')
    ]

    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    id_transaccion_pasarela = models.CharField(max_length=100, unique=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True, blank=True)
    pedido_personalizado = models.ForeignKey(PedidoPersonalizado, on_delete=models.SET_NULL, null=True, blank=True)
    solicitud_confeccion = models.ForeignKey(SolicitudConfeccion, on_delete=models.SET_NULL, null=True, blank=True)

class Imagen(models.Model):
    microempresa_satelite = models.ForeignKey(MicroempresaSatelite, on_delete=models.CASCADE)
    url = models.ImageField(upload_to='satelites/')
    descripcion = models.TextField(blank=True, null=True)

class Carrito(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)

    def get_subtotal(self):
        return self.producto.precio * self.cantidad

    # MODIFICACIÓN: Se eliminó la segunda definición redundante de 'cantidad'
    # La línea 'cantidad = models.IntegerField(default=1)' fue removida porque ya estaba definida arriba

class SolicitudServicio(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado')
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='solicitudes_servicio')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='solicitudes')
    microempresa_satelite = models.ForeignKey(MicroempresaSatelite, on_delete=models.CASCADE, related_name='solicitudes_recibidas')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_deseada = models.DateField()
    comentarios = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')

    # MODIFICACIÓN OPCIONAL: Añadimos un campo 'cantidad' para permitir múltiples unidades del servicio
    cantidad = models.IntegerField(default=1, help_text='Cantidad de unidades del servicio solicitadas')

    def __str__(self):
        return f'Solicitud de {self.cliente} - {self.servicio.nombre}'

    # MODIFICACIÓN: Corregimos el método get_subtotal para usar el precio del servicio
    def get_subtotal(self):
        from decimal import Decimal
        return Decimal(str(self.servicio.precio)) * Decimal(str(self.cantidad))