from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('resultado/<int:busqueda_id>/', views.resultado, name='resultado'),
    path('historial/', views.historial, name='historial'),
    path('borrar/<int:busqueda_id>/', views.borrar_consulta, name='borrar_consulta'),
]