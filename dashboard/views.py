import json
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate, TruncWeek
from core.models import Busqueda
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import calendar

@login_required
def panel_estadisticas(request):
    """
    Panel de control con estadísticas para superusuarios/admins
    """
    # Solo permitir acceso a superusuarios
    if not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Acceso denegado: Requiere permisos de staff")
    import logging
    logger = logging.getLogger(__name__)

    # Log para debug del problema de reverse
    logger.info("Intentando acceder a panel_estadisticas")
    logger.info(f"Nombre de la vista: {request.resolver_match.view_name if request.resolver_match else 'None'}")
    logger.info("Verificando configuración de URLs del dashboard")

    # Estadísticas generales
    total_busquedas = Busqueda.objects.count()
    total_usuarios = User.objects.count()
    # Usuarios con al menos una búsqueda (considerados "activos")
    busquedas_activos = User.objects.filter(busqueda__isnull=False).distinct().count()

    # Debug logging para validar la hipótesis
    logger.info(f"Total usuarios registrados: {total_usuarios}")
    logger.info(f"Usuarios con búsquedas (busquedas_activos): {busquedas_activos}")
    logger.info(f"Porcentaje esperado: {(busquedas_activos / total_usuarios * 100) if total_usuarios > 0 else 0}%")

    # Log detallado de usuarios
    todos_usuarios = list(User.objects.values_list('username', flat=True))
    logger.info(f"Lista de todos los usuarios registrados: {todos_usuarios}")

    usuarios_con_busquedas = list(User.objects.filter(busqueda__isnull=False).distinct().values_list('username', flat=True))
    logger.info(f"Usuarios con búsquedas: {usuarios_con_busquedas}")

    # Verificar si hay sesiones activas (aproximación)
    from django.contrib.sessions.models import Session
    sesiones_activas = Session.objects.filter(expire_date__gt=timezone.now()).count()
    logger.info(f"Número aproximado de sesiones activas: {sesiones_activas}")

    # Estadísticas de los últimos 30 días
    hace_30_dias = timezone.now() - timedelta(days=30)
    busquedas_mes = Busqueda.objects.filter(fecha_creacion__gte=hace_30_dias).count()
    usuarios_mes = (Busqueda.objects.filter(fecha_creacion__gte=hace_30_dias)
                   .values('usuario').distinct().count())

    # Top usuarios más activos (últimos 30 días)
    usuarios_activos = (Busqueda.objects.filter(fecha_creacion__gte=hace_30_dias)
                       .values('usuario__username', 'usuario__first_name', 'usuario__last_name')
                       .annotate(num_busquedas=Count('id'))
                       .order_by('-num_busquedas')[:10])

    # Búsquedas por día (últimos 7 días)
    hace_7_dias = timezone.now() - timedelta(days=7)
    busquedas_por_dia = (Busqueda.objects.filter(fecha_creacion__gte=hace_7_dias)
                        .annotate(fecha=TruncDate('fecha_creacion'))
                        .values('fecha')
                        .annotate(cantidad=Count('id'))
                        .order_by('fecha'))

    # Datos para el gráfico semanal
    fechas = []
    valores = []

    for i in range(6, -1, -1):
        fecha = timezone.now().date() - timedelta(days=i)
        cantidad = busquedas_por_dia.filter(fecha=fecha).first()
        fechas.append(fecha.strftime('%d/%m'))
        valores.append(cantidad['cantidad'] if cantidad else 0)

    # Búsquedas por semana (últimos 4 semaines)
    hace_28_dias = timezone.now() - timedelta(days=28)
    busquedas_por_semana = (Busqueda.objects.filter(fecha_creacion__gte=hace_28_dias)
                           .annotate(semana=TruncWeek('fecha_creacion'))
                           .values('semana')
                           .annotate(cantidad=Count('id'))
                           .order_by('semana'))

    # Estadísticas por categorías
    categorias = ['Automatización', 'Análisis de datos / predicción', 'Procesamiento de texto', 'Procesamiento de imágenes / video', 'Procesamiento de audio / voz', 'Generación de contenido', 'Recomendación / personalización', 'Optimización / decisión inteligente', 'Asistentes conversacionales']
    categorias_safe = ['automatizacion', 'analisis_datos_prediccion', 'procesamiento_texto', 'procesamiento_imagenes_video', 'procesamiento_audio_voz', 'generacion_contenido', 'recomendacion_personalizacion', 'optimizacion_decision_inteligente', 'asistentes_conversacionales']
    busquedas_por_categoria = {}
    for categoria, safe_key in zip(categorias, categorias_safe):
        busquedas_por_categoria[safe_key] = Busqueda.objects.filter(categoria=categoria).count()

    # Diccionario para nombres de display
    display_names = dict(zip(categorias_safe, categorias))

    # Estadísticas promedio
    promedio_puntuacion = 0
    distribucion_porcentaje = {'alta': 0, 'media': 0, 'baja': 0}

    # Inicializar busquedas_con_resultados para evitar NameError si no hay búsquedas
    busquedas_con_resultados = Busqueda.objects.none()

    logger.info(f"Busqueda.objects.exists(): {Busqueda.objects.exists()}")

    if Busqueda.objects.exists():
        # Calcular promedio de puntuaje general calculando average_viability on-the-fly
        busquedas_con_resultados = Busqueda.objects.exclude(resultado_llm__isnull=True).exclude(resultado_llm='')
        logger.info(f"busquedas_con_resultados definido con count: {busquedas_con_resultados.count()}")

        if busquedas_con_resultados:
            suma = 0
            count = 0
            for b in busquedas_con_resultados:
                try:
                    resultado = json.loads(b.resultado_llm)
                    if 'indices_clave' in resultado:
                        indices_clave = resultado['indices_clave']
                        adecuacion_ia = indices_clave.get('adecuacion_ia', {}).get('puntuacion', 0)
                        factibilidad_tecnica = indices_clave.get('factibilidad_tecnica', {}).get('puntuacion', 0)
                        impacto_potencial = indices_clave.get('impacto_potencial', {}).get('puntuacion', 0)
                        puntuacion = round((adecuacion_ia + factibilidad_tecnica + impacto_potencial) / 3)
                        suma += puntuacion
                        count += 1
                        # Clasificar por rangos: Alta (75%+), Media (50-74%), Baja (<50%)
                        if puntuacion >= 75:
                            distribucion_porcentaje['alta'] += 1
                        elif puntuacion >= 50:
                            distribucion_porcentaje['media'] += 1
                        else:
                            distribucion_porcentaje['baja'] += 1
                except (json.JSONDecodeError, TypeError, ZeroDivisionError):
                    continue

            promedio_puntuacion = suma / count if count > 0 else 0

    # Convertir distribucion_porcentaje a porcentajes
    total_con_puntuacion = sum(distribucion_porcentaje.values())
    if total_con_puntuacion > 0:
        for key in distribucion_porcentaje:
            distribucion_porcentaje[key] = round(
                (distribucion_porcentaje[key] / total_con_puntuacion) * 100, 1
            )

    # Datos para gráfico de distribución
    porcentaje_labels = ['Alta Viabilidad (75%+)', 'Media Viabilidad (50-74%)', 'Baja Viabilidad (<50%)']
    porcentaje_valores = [
        distribucion_porcentaje['alta'],
        distribucion_porcentaje['media'],
        distribucion_porcentaje['baja']
    ]

    # Cálculo de la tasa de conversión
    # Número de búsquedas con resultado_llm válido (no nulo y no vacío)
    busquedas_con_resultado = busquedas_con_resultados.count()
    # Porcentaje: (búsquedas_con_resultado / total_busquedas) * 100
    tasa_conversion = round((busquedas_con_resultado / total_busquedas) * 100, 1) if total_busquedas > 0 else 0.0

    contexto = {
        # Estadísticas generales
        'total_busquedas': total_busquedas,
        'total_usuarios': total_usuarios,
        'busquedas_activos': busquedas_activos,

        # Estadísticas del mes
        'busquedas_mes': busquedas_mes,
        'usuarios_mes': usuarios_mes,

        # Top usuarios
        'usuarios_activos': usuarios_activos,

        # Datos para gráficos
        'fechas_semanal': json.dumps(fechas),
        'valores_semanal': json.dumps(valores),
        'porcentaje_labels': json.dumps(porcentaje_labels),
        'porcentaje_valores': json.dumps(porcentaje_valores),

        # Estadísticas avanzadas
        'promedio_puntuacion': round(promedio_puntuacion, 1),
        'distribucion_porcentaje': distribucion_porcentaje,
        'tasa_conversion': tasa_conversion,

        # Estadísticas por categorías
        'busquedas_por_categoria': busquedas_por_categoria,
        'display_names': display_names,

        # Fecha actual
        'fecha_actual': timezone.now().date(),
    }

    return render(request, 'dashboard/panel.html', contexto)
