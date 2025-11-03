from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views, logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.contrib import messages
from django import forms
import logging

logger = logging.getLogger(__name__)

class UserRegisterForm(UserCreationForm):
    """
    Formulario personalizado para registro que incluye email
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CustomLoginView(auth_views.LoginView):
    """
    Vista de login personalizada que redirige usuarios autenticados
    """
    template_name = 'usuarios/login.html'

    def get(self, request, *args, **kwargs):
        """Redirige a usuarios ya autenticados"""
        logger.debug(f"CustomLoginView.get: user.is_authenticated = {request.user.is_authenticated}")
        if request.user.is_authenticated:
            logger.debug("Redirecting authenticated user from login page")
            return redirect('core:home')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        """Manejo adicional al login exitoso"""
        logger.debug("CustomLoginView.form_valid called")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Manejo adicional al login fallido"""
        logger.debug(f"CustomLoginView.form_invalid: form.errors = {form.errors}")
        logger.debug(f"CustomLoginView.form_invalid: form.non_field_errors = {form.non_field_errors()}")
        return super().form_invalid(form)

class RegisterView(CreateView):
    """
    Vista para el registro de nuevos usuarios
    """
    model = User
    form_class = UserRegisterForm
    template_name = 'usuarios/register.html'
    success_url = reverse_lazy('usuarios:login')

    def form_valid(self, form):
        """Método llamado cuando el formulario es válido"""
        logger.debug(f"RegisterView.form_valid: Saving user with email = {form.cleaned_data.get('email')}")
        response = super().form_valid(form)
        messages.success(self.request, f'Usuario {self.object.username} creado exitosamente. Ahora puedes iniciar sesión.')
        logger.debug(f"RegisterView.form_valid: User saved with email = {self.object.email}")
        return response

    def form_invalid(self, form):
        """Manejo adicional al registro fallido"""
        logger.debug(f"RegisterView.form_invalid: form.errors = {form.errors}")
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        """Redirige a usuarios ya autenticados"""
        logger.debug(f"RegisterView.get: user.is_authenticated = {request.user.is_authenticated}")
        if self.request.user.is_authenticated:
            logger.debug("Redirecting authenticated user from register page")
            return redirect('core:home')
        return super().get(request, *args, **kwargs)


def logout_view(request):
    """
    Vista personalizada de logout que acepta GET requests para la navegación
    """
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('core:home')
