from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Registro de usuarios
    path('register/', views.RegisterView.as_view(), name='register'),

    # Login usando la vista personalizada
    path('login/', views.CustomLoginView.as_view(), name='login'),

    # Logout personalizado que acepta GET requests
    path('logout/', views.logout_view, name='logout'),
]