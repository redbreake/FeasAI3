from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('panel/', views.panel_estadisticas, name='panel_estadisticas'),
    path('panel/', views.panel_estadisticas, name='panel'),
]