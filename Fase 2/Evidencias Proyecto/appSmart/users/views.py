"""
Views del módulo Users - Autenticación SmartERP.
"""
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib import messages


class CustomLoginView(LoginView):
    """
    Vista personalizada de login para SmartERP.
    Redirige al dashboard después del login exitoso.
    """
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirigir al dashboard después del login exitoso"""
        return reverse_lazy('inventory:home')
    
    def form_invalid(self, form):
        """Mostrar mensaje de error personalizado"""
        messages.error(self.request, 'Usuario o contraseña incorrectos.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """
    Vista personalizada de logout para SmartERP.
    Redirige al login después del logout.
    """
    next_page = reverse_lazy('users:login')
    
    def dispatch(self, request, *args, **kwargs):
        """Mostrar mensaje de logout exitoso"""
        if request.user.is_authenticated:
            messages.success(request, 'Sesión cerrada exitosamente.')
        return super().dispatch(request, *args, **kwargs)