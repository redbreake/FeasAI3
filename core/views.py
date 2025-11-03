"""
Vistas principales de la aplicación web FeasAI.

Este módulo contiene todas las vistas Django que manejan las interacciones
del usuario con el sistema de análisis de viabilidad de IA. Las vistas principales
gestionan el formulario de consulta, muestran resultados, mantienen el historial
de búsquedas y permiten la gestión de consultas anteriores.

Las vistas están protegidas con autenticación requerida (@login_required) para
asegurar que solo usuarios registrados puedan acceder al análisis de IA.
"""

import json  # Para manejar datos JSON en respuestas y base de datos
import requests  # Para posibles llamadas HTTP externas (aunque no se usa actualmente)
from django.shortcuts import render, redirect, get_object_or_404  # Utilidades básicas de Django
from django.contrib.auth.decorators import login_required  # Decorador para vistas que requieren login
from django.contrib import messages  # Sistema de mensajes de Django
from django.contrib.auth.models import User  # Modelo de usuario de Django
from django.http import JsonResponse  # Para respuestas JSON
from django.views.decorators.http import require_POST  # Decorador para métodos POST
from django.db.models import Count  # Para agregaciones en consultas de base de datos
from .models import Busqueda  # Modelo de búsqueda local
from .llm_service import analizar_viabilidad  # Servicio de IA principal
from .utils import clasificar_consulta  # Utilidad para clasificar consultas

# Nota: Las funciones de prueba anteriores fueron reemplazadas por el servicio unificado de Gemini/Cerebras

@login_required
def home(request):
    """
    Vista principal y más importante de la aplicación.

    Maneja tanto la presentación del formulario de consulta como el procesamiento
    de nuevas consultas de viabilidad de IA. Esta vista es el punto de entrada
    principal donde los usuarios describen sus problemas o proyectos para
    obtener análisis detallados de aplicabilidad de inteligencia artificial.
    """
    if request.method == 'POST':
        # Extraer y limpiar el problema del formulario
        problema = request.POST.get('problema', '').strip()

        # Validación básica inicial
        if not problema:
            messages.error(request, 'Por favor, describe el problema que quieres analizar.')
            return redirect('core:home')

        try:
            # Validaciones exhaustivas del input del usuario
            # Es crítico validar aquí porque los modelos de IA pueden fallar con inputs inválidos
            if not problema or not isinstance(problema, str) or problema.strip() == "":
                messages.error(request, 'Por favor, describe el problema que quieres analizar con más detalle.')
                return redirect('core:home')

            if len(problema.strip()) < 10:
                messages.error(request, 'La descripción del problema debe tener al menos 10 caracteres.')
                return redirect('core:home')

            # Determinar qué modelo de IA usar (usuario puede elegir entre opciones disponibles)
            model = request.POST.get('model', 'gemini').strip().lower()
            if model not in ['gemini', 'cerebras']:
                model = 'gemini'  # Valor por defecto si el usuario envía algo inválido

            # Llamada principal al servicio de IA - aquí es donde ocurre el análisis real
            resultado_llm = analizar_viabilidad(model, problema)

            # Verificar si la llamada a la IA fue exitosa o hubo algún error
            if "error" in resultado_llm:
                messages.error(request, f"Error en la consulta: {resultado_llm['error']}")
                return redirect('core:home')

            # Clasificación automática del tipo de consulta para estadísticas
            categoria = clasificar_consulta(problema)

            # Persistencia en base de datos: guardar toda la información de la búsqueda
            busqueda = Busqueda.objects.create(
                usuario=request.user,  # Usuario autenticado que realizó la consulta
                texto_problema=problema,  # El problema original descrito por el usuario
                modelo=model,  # Qué modelo de IA se usó para el análisis
                categoria=categoria,  # Clasificación automática del tipo de problema
                resultado_llm=json.dumps(resultado_llm)  # Resultado completo convertido a JSON para almacenar
            )
    
            # Éxito: redirigir al usuario a ver los resultados detallados
            messages.success(request, 'Análisis completado exitosamente con IA avanzada.')
            return redirect('core:resultado', busqueda_id=busqueda.id)

        except Exception as e:
            # Manejo de errores genérico - cualquier excepción durante el proceso
            print(f"Error al procesar la consulta: {e}")
            messages.error(request, 'Hubo un error al conectar con el servicio de IA. Inténtalo nuevamente.')
            return redirect('core:home')

    # Método GET: simplemente mostrar el formulario de consulta vacío
    return render(request, 'core/home.html')

@login_required
def resultado(request, busqueda_id):
    """
    Vista que muestra los resultados detallados del análisis de viabilidad.

    Esta vista toma el ID de una búsqueda guardada y presenta al usuario
    un análisis completo y estructurado generado por la IA. Incluye
    puntuaciones, recomendaciones, alternativas y datos para visualización
    en gráficos, todo calculado por modelos de lenguaje avanzados.
    """
    # Obtener la búsqueda específica del usuario (seguridad: solo puede ver sus propias búsquedas)
    busqueda = get_object_or_404(Busqueda, id=busqueda_id, usuario=request.user)

    try:
        # Convertir el JSON almacenado de vuelta a diccionario Python para usar en template
        resultado = json.loads(busqueda.resultado_llm)

        # Cálculo de métrica adicional: promedio de viabilidad basado en los tres índices clave
        if 'indices_clave' in resultado:
            indices_clave = resultado['indices_clave']
            adecuacion_ia = indices_clave.get('adecuacion_ia', {}).get('puntuacion', 0)
            factibilidad_tecnica = indices_clave.get('factibilidad_tecnica', {}).get('puntuacion', 0)
            impacto_potencial = indices_clave.get('impacto_potencial', {}).get('puntuacion', 0)
            # Promedio simple de las tres puntuaciones principales
            average = round((adecuacion_ia + factibilidad_tecnica + impacto_potencial) / 3)
            resultado['average_viability'] = average

    except json.JSONDecodeError:
        # Error si el JSON almacenado está corrupto (caso muy raro)
        messages.error(request, 'Error al cargar los resultados.')
        return redirect('core:home')  # Redirigir a home en lugar de 'subir' que no existe

    # Renderizar template con toda la información del análisis
    return render(request, 'core/resultado.html', {
        'busqueda': busqueda,  # Información de la búsqueda (usuario, fecha, modelo usado, etc.)
        'resultado': resultado  # Análisis completo generado por la IA
    })

@login_required
def historial(request):
    """
    Vista que muestra el historial completo de consultas del usuario.

    Permite a los usuarios revisar sus análisis anteriores, ver patrones
    en sus consultas y acceder nuevamente a resultados previos. Incluye
    estadísticas sobre tipos de problemas más consultados.
    """
    # Obtener todas las consultas del usuario actual, ordenadas por fecha descendente
    consultas = Busqueda.objects.filter(usuario=request.user)
    consultas = consultas.order_by('-fecha_creacion')

    # Generar estadísticas de uso por categoría para análisis de patrones
    estadisticas_categoria = Busqueda.objects.filter(usuario=request.user).values('categoria').annotate(
        total=Count('categoria')  # Contar ocurrencias de cada categoría
    ).order_by('-total')  # Ordenar por frecuencia descendente

    # Calcular porcentajes para mostrar distribución de consultas por tipo
    total_consultas_usuario = Busqueda.objects.filter(usuario=request.user).count()
    for estadistica in estadisticas_categoria:
        estadistica['porcentaje'] = round((estadistica['total'] / total_consultas_usuario) * 100) if total_consultas_usuario > 0 else 0

    # Mostrar historial completo con estadísticas de uso
    return render(request, 'core/historial.html', {
        'consultas': consultas,  # Lista completa de búsquedas del usuario
        'estadisticas_categoria': estadisticas_categoria  # Estadísticas por categoría
    })

@login_required
@require_POST
def borrar_consulta(request, busqueda_id):
    """
    Vista que permite eliminar una consulta específica del historial.

    Esta función asegura que solo el propietario de la consulta pueda
    eliminarla y proporciona feedback al usuario sobre la operación.
    """
    # Verificar que la búsqueda existe y pertenece al usuario actual
    busqueda = get_object_or_404(Busqueda, id=busqueda_id, usuario=request.user)
    busqueda.delete()  # Eliminar permanentemente de la base de datos
    messages.success(request, 'Consulta eliminada exitosamente.')
    return redirect('core:historial')  # Redirigir de vuelta al historial
