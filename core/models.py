"""
Modelos de datos para la aplicación FeasAI.

Este archivo define las estructuras de datos que se almacenan en la base de datos,
principalmente el modelo Busqueda que guarda toda la información de las consultas
de viabilidad de IA realizadas por los usuarios, incluyendo resultados, categorías
y metadatos asociados.
"""

from django.db import models  # Para definir modelos de base de datos Django
from django.contrib.auth.models import User  # Modelo de usuario estándar de Django


class Busqueda(models.Model):
    """
    Modelo principal que representa una consulta de viabilidad de IA realizada por un usuario.

    Este modelo almacena toda la información relevante de cada análisis, desde el
    problema original hasta los resultados completos generados por los modelos de IA.
    Es fundamental para mantener el historial de consultas y permitir análisis
    estadísticos sobre el uso del sistema.
    """
    # Relación con el usuario que realizó la consulta - eliminación en cascada
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # Si se elimina el usuario, se eliminan todas sus búsquedas
        help_text="Usuario que realizó la búsqueda"
    )

    # El problema o necesidad descrita por el usuario que se quiere analizar
    texto_problema = models.TextField(
        help_text="El problema o consulta introducida por el usuario"
    )

    # Modelo de IA utilizado para generar el análisis
    modelo = models.CharField(
        max_length=10,
        choices=[('gemini', 'Gemini'), ('cerebras', 'Cerebras')],  # Solo dos opciones disponibles
        default='gemini',  # Gemini como opción predeterminada
        help_text="Modelo LLM utilizado para la consulta"
    )

    # Resultado completo del modelo de IA almacenado como JSON estructurado
    resultado_llm = models.JSONField(
        null=True,  # Permite valores nulos si la consulta falló
        blank=True,  # Permite formularios vacíos
        help_text="Respuesta completa del LLM en formato JSON"
    )

    # Clasificación automática del tipo de problema/IA basado en el contenido
    categoria = models.CharField(
        max_length=50,
        choices=[
            ('Automatización', 'Automatización'),
            ('Análisis de datos / predicción', 'Análisis de datos / predicción'),
            ('Procesamiento de texto', 'Procesamiento de texto'),
            ('Procesamiento de imágenes / video', 'Procesamiento de imágenes / video'),
            ('Procesamiento de audio / voz', 'Procesamiento de audio / voz'),
            ('Generación de contenido', 'Generación de contenido'),
            ('Recomendación / personalización', 'Recomendación / personalización'),
            ('Optimización / decisión inteligente', 'Optimización / decisión inteligente'),
            ('Asistentes conversacionales', 'Asistentes conversacionales')
        ],
        default='Automatización',  # Categoría por defecto
        help_text="Categoría de la consulta"
    )

    # Timestamp automático de cuando se creó la búsqueda
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,  # Se establece automáticamente al crear el registro
        help_text="Fecha y hora en que se realizó la búsqueda"
    )

    def __str__(self):
        """
        Representación legible del objeto para uso en admin y debugging.

        Muestra el nombre de usuario y los primeros 50 caracteres del problema,
        lo cual es útil para identificar búsquedas específicas sin mostrar
        texto excesivamente largo.
        """
        return f"Búsqueda de {self.usuario.username} - {self.texto_problema[:50]}..."

    class Meta:
        """
        Metadatos del modelo que afectan su comportamiento en Django.

        Define el ordenamiento por defecto, nombres legibles para la interfaz
        de administración y otras configuraciones del modelo.
        """
        ordering = ['-fecha_creacion']  # Las búsquedas más recientes primero
        verbose_name = "Búsqueda"  # Nombre singular en español
        verbose_name_plural = "Búsquedas"  # Nombre plural en español
