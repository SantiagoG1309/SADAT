import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import CustomUserCreationForm, ProductForm, ServiceForm, UserProfileForm, AdminUserEditForm
from .models import User, Producto, Carrito, CarritoItem, MicroempresaIntegral, Cliente, MicroempresaSatelite, Servicio, SolicitudServicio
from django.db import transaction
from django.db.models import F

# Decorador personalizado para restringir acceso a Empresa Integral
def empresa_integral_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_integral():
            return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

def catalogo_integral(request):
    empresas = MicroempresaIntegral.objects.all()
    return render(request, 'core/catalogo_integral.html', {'empresas': empresas})

def catalogo_satelite(request):
    empresas_satelite = MicroempresaSatelite.objects.all()
    return render(request, 'core/catalogo_satelite.html', {'empresas_satelite': empresas_satelite})

def catalogo_productos_integral(request, empresa_id):
    empresa = get_object_or_404(MicroempresaIntegral, id=empresa_id)
    productos = Producto.objects.filter(microempresa_integral=empresa)
    
    # Filtrar por búsqueda
    search_query = request.GET.get('search', '')
    if search_query:
        productos = productos.filter(nombre__icontains=search_query)
    
    # Filtrar por categoría
    categoria = request.GET.get('categoria', '')
    if categoria:
        productos = productos.filter(categoria=categoria)
    
    # Ordenar productos
    orden = request.GET.get('orden', '')
    if orden == 'precio_asc':
        productos = productos.order_by('precio')
    elif orden == 'precio_desc':
        productos = productos.order_by('-precio')
    elif orden == 'nombre_asc':
        productos = productos.order_by('nombre')
    elif orden == 'nombre_desc':
        productos = productos.order_by('-nombre')
    
    context = {
        'empresa': empresa,
        'productos': productos,
        'search_query': search_query,
        'categoria_seleccionada': categoria,
        'orden_seleccionado': orden
    }
    
    return render(request, 'core/catalogo_productos_integral.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.is_cliente():
                cliente = Cliente.objects.create(usuario=user)
                Carrito.objects.create(cliente=cliente)  # Crear carrito para el cliente
            elif user.is_integral():
                MicroempresaIntegral.objects.create(
                    usuario=user,
                    direccion=user.address,
                    titulo=form.cleaned_data.get('titulo_empresa', ''),
                    logo=form.cleaned_data.get('logo_empresa'),
                    eslogan=form.cleaned_data.get('eslogan_empresa', ''),
                    descripcion=form.cleaned_data.get('descripcion_empresa', '')
                )
            elif user.is_satelite():
                MicroempresaSatelite.objects.create(
                    usuario=user,
                    direccion=user.address,
                    titulo=form.cleaned_data.get('titulo_empresa', ''),
                    logo=form.cleaned_data.get('logo_empresa'),
                    eslogan=form.cleaned_data.get('eslogan_empresa', ''),
                    descripcion=form.cleaned_data.get('descripcion_empresa', '')
                )
            messages.success(request, '¡Registro exitoso!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def home(request):
    user = request.user
    context = {'user': user}
    
    if user.is_integral():
        try:
            integral = MicroempresaIntegral.objects.get(usuario=user)
            products = Producto.objects.filter(microempresa_integral=integral)
            context['products'] = products
            return render(request, 'core/integral_home.html', context)
        except MicroempresaIntegral.DoesNotExist:
            messages.error(request, 'No se encontró la información de tu microempresa')
            return redirect('login')
    
    elif user.is_satelite():
        try:
            satelite = MicroempresaSatelite.objects.get(usuario=user)
            services = Servicio.objects.filter(microempresa_satelite=satelite)
            solicitudes_pendientes = SolicitudServicio.objects.filter(
                microempresa_satelite=satelite
            ).order_by('-fecha_solicitud')
            context.update({
                'services': services,
                'solicitudes_pendientes': solicitudes_pendientes
            })
            return render(request, 'core/satelite_home.html', context)
        except MicroempresaSatelite.DoesNotExist:
            messages.error(request, 'No se encontró la información de tu microempresa satélite')
            return redirect('login')
    
    elif user.is_cliente():
        # Obtener todas las empresas integrales y satélites
        empresas_integrales = MicroempresaIntegral.objects.all()
        empresas_satelite = MicroempresaSatelite.objects.all()
        
        # Si se especifica una empresa integral, mostrar sus productos
        empresa_id = request.GET.get('empresa')
        if empresa_id:
            empresa = get_object_or_404(MicroempresaIntegral, id=empresa_id)
            products = Producto.objects.filter(microempresa_integral=empresa)
            context.update({
                'empresa_actual': empresa,
                'products': products
            })
        # Si se especifica una empresa satélite, mostrar sus servicios
        satelite_id = request.GET.get('satelite')
        if satelite_id:
            satelite = get_object_or_404(MicroempresaSatelite, id=satelite_id)
            servicios = Servicio.objects.filter(microempresa_satelite=satelite)
            return render(request, 'core/satelite_services.html', {
                'satelite': satelite,
                'servicios': servicios
            })
        else:
            context.update({
                'empresas': empresas_integrales,
                'empresas_satelite': empresas_satelite
            })
        return render(request, 'core/cliente_home.html', context)
    
    elif user.is_system_admin():
        # Obtener estadísticas del sistema
        context.update({
            'total_users': User.objects.count(),
            'total_products': Producto.objects.count(),
            'total_services': Servicio.objects.count(),
            'total_orders': CarritoItem.objects.count(),
            'users': User.objects.all().order_by('-date_joined'),
            'integrales': MicroempresaIntegral.objects.all().count(),
            'satelites': MicroempresaSatelite.objects.all().count()
        })
        return render(request, 'core/system_admin_home.html', context)
    
    return redirect('login')

@login_required
def add_product(request):
    if not request.user.is_integral():
        messages.error(request, 'No tienes permiso para agregar productos')
        return redirect('home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            integral = MicroempresaIntegral.objects.get(usuario=request.user)
            producto.microempresa_integral = integral
            producto.save()
            messages.success(request, 'Producto agregado exitosamente')
            return redirect('home')
    else:
        form = ProductForm()
    
    return render(request, 'core/product_form.html', {'form': form, 'action': 'Agregar'})

@login_required
def edit_product(request, product_id):
    if not request.user.is_integral():
        messages.error(request, 'Acceso denegado')
        return redirect('home')
    
    integral = MicroempresaIntegral.objects.get(usuario=request.user)
    producto = get_object_or_404(Producto, id=product_id, microempresa_integral=integral)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('home')
    else:
        form = ProductForm(instance=producto)
    
    return render(request, 'core/product_form.html', {'form': form, 'action': 'Editar'})

@login_required
def delete_product(request, product_id):
    if not request.user.is_integral():
        messages.error(request, 'Acceso denegado')
        return redirect('home')
    
    integral = MicroempresaIntegral.objects.get(usuario=request.user)
    producto = get_object_or_404(Producto, id=product_id, microempresa_integral=integral)
    producto.delete()
    messages.success(request, 'Producto eliminado exitosamente')
    return redirect('home')

@login_required
def cart(request):
    if not request.user.is_cliente():
        messages.error(request, 'Solo los clientes pueden acceder al carrito')
        return redirect('home')
    
    cliente = Cliente.objects.get(usuario=request.user)
    carrito, created = Carrito.objects.get_or_create(cliente=cliente)
    items = CarritoItem.objects.filter(carrito=carrito).select_related('producto', 'producto__microempresa_integral', 'producto__microempresa_integral__usuario')
    
    from decimal import Decimal
    subtotal = Decimal('0')
    for item in items:
        item_subtotal = item.get_subtotal()
        if item_subtotal is not None:
            subtotal += item_subtotal
    
    iva = subtotal * Decimal('0.19')
    total = subtotal + iva
    
    return render(request, 'core/cart.html', {
        'items': items,
        'cart_items': items,
        'subtotal': subtotal,
        'iva': iva,
        'total': total
    })

@csrf_exempt
@require_POST
@login_required
def add_to_cart(request, product_id):
    if not request.user.is_cliente():
        return JsonResponse({'error': 'Solo los clientes pueden agregar productos al carrito'}, status=403)
    
    try:
        data = json.loads(request.body)
        cantidad = int(data.get('quantity', 1))
        if cantidad <= 0:
            return JsonResponse({'error': 'La cantidad debe ser mayor a 0'}, status=400)
        
        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(id=product_id)
            cliente = Cliente.objects.get(usuario=request.user)
            carrito, _ = Carrito.objects.get_or_create(cliente=cliente)
            
            item, created = CarritoItem.objects.get_or_create(
                carrito=carrito,
                producto=producto,
                defaults={'cantidad': 0}
            )
            
            if cantidad > producto.stock:
                return JsonResponse({
                    'error': f'La cantidad solicitada excede el stock disponible. Stock actual: {producto.stock}',
                    'current_stock': producto.stock,
                    'product_id': product_id
                }, status=400)
            
            nueva_cantidad = item.cantidad + cantidad
            item.cantidad = nueva_cantidad
            item.save()
            
            producto.stock -= cantidad
            producto.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Producto agregado al carrito exitosamente',
                'new_stock': producto.stock,
                'product_id': product_id,
                'cart_quantity': nueva_cantidad
            })
            
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado', 'product_id': product_id}, status=404)
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Usuario no es un cliente', 'product_id': product_id}, status=403)
    except ValueError:
        return JsonResponse({'error': 'La cantidad ingresada no es válida', 'product_id': product_id}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error al procesar la solicitud: {str(e)}', 'product_id': product_id}, status=500)

@login_required
def update_cart(request, product_id):
    if not request.user.is_cliente():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        with transaction.atomic():
            cantidad = int(request.POST.get('cantidad', 0))
            if cantidad < 0:
                return JsonResponse({'error': 'Cantidad inválida'}, status=400)
            
            cliente = Cliente.objects.get(usuario=request.user)
            carrito = Carrito.objects.get(cliente=cliente)
            
            item = CarritoItem.objects.select_related('producto').get(carrito=carrito, producto_id=product_id)
            producto = Producto.objects.select_for_update().get(id=product_id)
            
            if cantidad > 0 and cantidad > (producto.stock + item.cantidad):
                return JsonResponse({'error': 'No hay suficiente stock disponible'}, status=400)
            
            if cantidad == 0:
                producto.stock = F('stock') + item.cantidad
                producto.save()
                item.delete()
            else:
                diferencia = cantidad - item.cantidad
                if diferencia != 0:
                    producto.stock = F('stock') - diferencia
                    producto.save()
                item.cantidad = cantidad
                item.save()
            
            producto.refresh_from_db()
            
            return JsonResponse({
                'message': 'Carrito actualizado',
                'new_stock': producto.stock
            })
    except CarritoItem.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado en el carrito'}, status=404)
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Cantidad inválida'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Error al actualizar el carrito'}, status=500)

@login_required
def remove_from_cart(request, product_id):
    if not request.user.is_cliente():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        with transaction.atomic():
            cliente = Cliente.objects.get(usuario=request.user)
            carrito = Carrito.objects.get(cliente=cliente)
            
            item = CarritoItem.objects.select_related('producto').get(carrito=carrito, producto_id=product_id)
            producto = Producto.objects.select_for_update().get(id=product_id)
            
            producto.stock = F('stock') + item.cantidad
            producto.save()
            
            item.delete()
            
            producto.refresh_from_db()
            
            return JsonResponse({
                'message': 'Producto eliminado del carrito',
                'new_stock': producto.stock
            })
    except CarritoItem.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado en el carrito'}, status=404)
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Error al eliminar el producto del carrito'}, status=500)

@login_required
def profile(request):
    return render(request, 'core/profile.html', {'user': request.user})

@login_required
def add_service(request):
    if not request.user.is_satelite():
        messages.error(request, 'No tienes permiso para agregar servicios')
        return redirect('home')
    
    try:
        satelite = MicroempresaSatelite.objects.get(usuario=request.user)
    except MicroempresaSatelite.DoesNotExist:
        messages.error(request, 'No se encontró la información de tu microempresa satélite')
        return redirect('home')
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            servicio = form.save(commit=False)
            servicio.microempresa_satelite = satelite
            servicio.save()
            messages.success(request, 'Servicio agregado exitosamente')
            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = ServiceForm()
    
    return render(request, 'core/service_form.html', {'form': form, 'action': 'Agregar'})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente')
            return redirect('home')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'core/edit_profile.html', {'form': form})

@login_required
def edit_service(request, service_id):
    if not request.user.is_satelite():
        messages.error(request, 'No tienes permiso para editar servicios')
        return redirect('home')
    
    servicio = get_object_or_404(Servicio, id=service_id)
    satelite = MicroempresaSatelite.objects.get(usuario=request.user)
    
    if servicio.microempresa_satelite != satelite:
        messages.error(request, 'No tienes permiso para editar este servicio')
        return redirect('home')
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio actualizado exitosamente')
            return redirect('home')
    else:
        form = ServiceForm(instance=servicio)
    
    return render(request, 'core/service_form.html', {'form': form, 'action': 'Editar'})

@login_required
def delete_service(request, service_id):
    if not request.user.is_satelite():
        messages.error(request, 'No tienes permiso para eliminar servicios')
        return redirect('home')
    
    servicio = get_object_or_404(Servicio, id=service_id)
    satelite = MicroempresaSatelite.objects.get(usuario=request.user)
    
    if servicio.microempresa_satelite != satelite:
        messages.error(request, 'No tienes permiso para eliminar este servicio')
        return redirect('home')
    
    servicio.delete()
    messages.success(request, 'Servicio eliminado exitosamente')
    return redirect('home')

@login_required
def system_admin_edit_user(request, user_id):
    if not request.user.is_system_admin():
        messages.error(request, 'No tienes permiso para editar usuarios')
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        if 'delete' in request.POST:
            if user != request.user:
                user.delete()
                messages.success(request, f'Usuario {user.username} eliminado exitosamente')
                return redirect('home')
            else:
                messages.error(request, 'No puedes eliminar tu propia cuenta')
        
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente')
            return redirect('home')
    else:
        form = AdminUserEditForm(instance=user)
    
    return render(request, 'core/system_admin_edit_user.html', {'form': form, 'user_to_edit': user})

@login_required
def system_admin_toggle_user(request, user_id):
    if not request.user.is_system_admin():
        messages.error(request, 'No tienes permiso para modificar usuarios')
        return redirect('home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        if user != request.user:
            user.is_active = not user.is_active
            user.save()
            action = 'activado' if user.is_active else 'desactivado'
            messages.success(request, f'Usuario {user.username} {action} exitosamente')
        else:
            messages.error(request, 'No puedes desactivar tu propia cuenta')
    
    return redirect('home')

@login_required
def solicitar_servicio(request, servicio_id):
    if not request.user.is_cliente():
        messages.error(request, 'Solo los clientes pueden solicitar servicios')
        return redirect('home')
    
    servicio = get_object_or_404(Servicio, id=servicio_id)
    satelite = servicio.microempresa_satelite
    cliente = Cliente.objects.get(usuario=request.user)
    
    if request.method == 'POST':
        fecha_deseada = request.POST.get('fecha_deseada')
        comentarios = request.POST.get('comentarios', '')
        
        if not fecha_deseada:
            messages.error(request, 'La fecha deseada es requerida')
            return render(request, 'core/solicitar_servicio.html', {
                'servicio': servicio,
                'satelite': satelite
            })
        
        try:
            solicitud = SolicitudServicio.objects.create(
                cliente=cliente,
                servicio=servicio,
                microempresa_satelite=satelite,
                fecha_deseada=fecha_deseada,
                comentarios=comentarios,
                estado='PENDIENTE'
            )
            messages.success(request, 'Solicitud de servicio enviada exitosamente')
            return redirect('mis_solicitudes')
        except Exception as e:
            messages.error(request, 'Error al crear la solicitud de servicio')
            return render(request, 'core/solicitar_servicio.html', {
                'servicio': servicio,
                'satelite': satelite
            })
    
    return render(request, 'core/solicitar_servicio.html', {
        'servicio': servicio,
        'satelite': satelite
    })

@login_required
def mis_solicitudes(request):
    if not request.user.is_cliente():
        messages.error(request, 'Acceso no autorizado')
        return redirect('home')
    
    cliente = Cliente.objects.get(usuario=request.user)
    solicitudes = SolicitudServicio.objects.filter(cliente=cliente).order_by('-fecha_solicitud')
    
    return render(request, 'core/mis_solicitudes.html', {
        'solicitudes': solicitudes
    })

@login_required
def cancelar_solicitud(request, solicitud_id):
    if not request.user.is_cliente():
        messages.error(request, 'Acceso no autorizado')
        return redirect('home')
    
    solicitud = get_object_or_404(SolicitudServicio, id=solicitud_id)
    if solicitud.cliente.usuario != request.user:
        messages.error(request, 'No tienes permiso para cancelar esta solicitud')
        return redirect('mis_solicitudes')
    
    if solicitud.estado == 'PENDIENTE':
        solicitud.estado = 'CANCELADO'
        solicitud.save()
        messages.success(request, 'Solicitud cancelada exitosamente')
    else:
        messages.error(request, 'No se puede cancelar una solicitud que ya está en proceso')
    
    return redirect('mis_solicitudes')

@login_required
def procesar_solicitud(request, solicitud_id, estado):
    if not request.user.is_satelite():
        messages.error(request, 'Acceso no autorizado')
        return redirect('home')
    
    solicitud = get_object_or_404(SolicitudServicio, id=solicitud_id)
    if solicitud.microempresa_satelite.usuario != request.user:
        messages.error(request, 'No tienes permiso para gestionar esta solicitud')
        return redirect('home')
    
    if solicitud.estado != 'PENDIENTE':
        messages.error(request, 'Esta solicitud no puede ser procesada')
        return redirect('home')
    
    if estado == 'aceptada':
        solicitud.estado = 'EN_PROCESO'
        mensaje = 'Solicitud aceptada exitosamente'
    elif estado == 'rechazada':
        solicitud.estado = 'RECHAZADA'
        mensaje = 'Solicitud rechazada exitosamente'
    else:
        messages.error(request, 'Estado no válido')
        return redirect('home')
    
    solicitud.save()
    messages.success(request, mensaje)
    return redirect('home')

@login_required
def system_admin_transactions(request):
    if not request.user.is_system_admin():
        messages.error(request, 'No tienes permiso para ver transacciones')
        return redirect('home')
    
    transactions = TransaccionPago.objects.all().order_by('-fecha')
    return render(request, 'core/system_admin_transactions.html', {
        'transactions': transactions
    })

@login_required
def system_admin_companies(request):
    if not request.user.is_system_admin():
        messages.error(request, 'No tienes permiso para ver empresas')
        return redirect('home')
    
    integrales = MicroempresaIntegral.objects.all().select_related('usuario')
    satelites = MicroempresaSatelite.objects.all().select_related('usuario')
    
    return render(request, 'core/system_admin_companies.html', {
        'integrales': integrales,
        'satelites': satelites
    })

# Vista para actualizar el stock desde el panel de control de Empresa Integral
@csrf_exempt
@require_POST
@login_required
@empresa_integral_required
def update_stock(request, product_id):
    try:
        integral = MicroempresaIntegral.objects.get(usuario=request.user)
        product = get_object_or_404(Producto, id=product_id, microempresa_integral=integral)
        
        data = json.loads(request.body)
        new_stock = int(data.get('stock', 0))
        
        if new_stock < 0:
            return JsonResponse({'success': False, 'error': 'El stock no puede ser negativo'}, status=400)
        
        product.stock = new_stock
        product.save()
        
        return JsonResponse({
            'success': True,
            'new_stock': product.stock
        })
    except Producto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Producto no encontrado'}, status=404)
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Stock inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# Nueva vista para vaciar el carrito (Cancelar Pedido)
@login_required
def clear_cart(request):
    if not request.user.is_cliente():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        with transaction.atomic():
            cliente = Cliente.objects.get(usuario=request.user)
            carrito = Carrito.objects.get(cliente=cliente)
            
            # Obtener todos los items del carrito con bloqueo
            items = CarritoItem.objects.filter(carrito=carrito).select_related('producto')
            for item in items:
                producto = Producto.objects.select_for_update().get(id=item.producto.id)
                # Devolver el stock
                producto.stock = F('stock') + item.cantidad
                producto.save()
            
            # Eliminar todos los items del carrito
            items.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Carrito vaciado exitosamente'
            })
    except Carrito.DoesNotExist:
        return JsonResponse({'error': 'Carrito no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Error al vaciar el carrito'}, status=500)