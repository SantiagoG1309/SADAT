from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Rutas de catálogos
    path('catalogo/integral/', views.catalogo_integral, name='catalogo_integral'),
    path('catalogo/integral/<int:empresa_id>/', views.catalogo_productos_integral, name='catalogo_productos_integral'),
    path('catalogo/satelite/', views.catalogo_satelite, name='catalogo_satelite'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    # Rutas para gestión de productos
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    # Rutas para gestión de servicios
    path('services/add/', views.add_service, name='add_service'),
    path('services/edit/<int:service_id>/', views.edit_service, name='edit_service'),
    path('services/delete/<int:service_id>/', views.delete_service, name='delete_service'),
    # Rutas para el carrito
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    # Nueva ruta para vaciar el carrito
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    # Rutas del administrador del sistema
    path('system-admin/users/edit/<int:user_id>/', views.system_admin_edit_user, name='system_admin_edit_user'),
    path('system-admin/users/toggle/<int:user_id>/', views.system_admin_toggle_user, name='system_admin_toggle_user'),
    # Rutas para gestión de solicitudes de servicio
    path('solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
    path('solicitudes/cancelar/<int:solicitud_id>/', views.cancelar_solicitud, name='cancelar_solicitud'),
    path('solicitudes/procesar/<int:solicitud_id>/<str:estado>/', views.procesar_solicitud, name='procesar_solicitud'),
    path('system-admin/transactions/', views.system_admin_transactions, name='system_admin_transactions'),
    path('system-admin/companies/', views.system_admin_companies, name='system_admin_companies'),
    path('system-admin/', views.home, name='system_admin_home'),
    # Ruta para solicitar servicios
    path('solicitar-servicio/<int:servicio_id>/', views.solicitar_servicio, name='solicitar_servicio'),
    # Ruta para actualizar el stock
    path('integral/update_stock/<int:product_id>/', views.update_stock, name='update_stock'),
]