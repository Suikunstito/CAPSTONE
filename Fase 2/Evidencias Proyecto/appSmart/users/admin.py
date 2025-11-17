"""
Administración de modelos del módulo Users en Django Admin.
Personalización de usuarios y permisos.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Desregistrar el User admin por defecto
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Administración personalizada de Usuarios"""
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'is_staff', 'is_active', 'date_joined'
    ]
    
    list_filter = [
        'is_staff', 'is_superuser', 'is_active', 'date_joined'
    ]
    
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = (
        ('Credenciales', {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permisos', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Crear Usuario', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    list_per_page = 25
    date_hierarchy = 'date_joined'


# Personalizar el sitio de administración
admin.site.site_header = "SmartERP - Administración"
admin.site.site_title = "SmartERP Admin"
admin.site.index_title = "Panel de Administración SmartERP"
