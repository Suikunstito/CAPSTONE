"""
Vistas del dominio Users - Autenticación
Migrado desde productos/views.py (CustomLoginView)
"""
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView


class CustomLoginView(LoginView):
    """
    Vista de login personalizada con redirect automático
    si el usuario ya está autenticado
    """
    template_name = 'users/login.html'  # Template reubicado

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')  # Redirect a dashboard como antes
        return super().dispatch(request, *args, **kwargs)