from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Producto, Servicio

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        label='Tipo de Usuario',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        label='Teléfono',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        label='Dirección',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    # Campos adicionales para empresas
    titulo_empresa = forms.CharField(
        max_length=100,
        required=False,
        label='Título de la Empresa',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    logo_empresa = forms.ImageField(
        required=False,
        label='Logo de la Empresa',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    eslogan_empresa = forms.CharField(
        max_length=200,
        required=False,
        label='Eslogan de la Empresa',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    descripcion_empresa = forms.CharField(
        required=False,
        label='Descripción de la Empresa',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'phone', 'address', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

class ProductForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'imagen', 'stock']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'precio', 'tipo_servicio']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'tipo_servicio': forms.Select(attrs={'class': 'form-select'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Electrónico',
            'phone': 'Teléfono',
            'address': 'Dirección',
        }

class AdminUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'phone', 'address', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Electrónico',
            'role': 'Rol de Usuario',
            'phone': 'Teléfono',
            'address': 'Dirección',
            'is_active': 'Usuario Activo',
        }