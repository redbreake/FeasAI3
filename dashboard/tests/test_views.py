import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from core.models import Busqueda


class DashboardViewsTest(TestCase):
    """Test suite for dashboard app views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
        self.client.login(username='admin', password='admin123')

        # Create test users and busquedas
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )

        # Create busquedas with different dates and categories
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)

        Busqueda.objects.create(
            usuario=self.user1,
            texto_problema='Query 1',
            categoria='Automatización',
            fecha_creacion=now
        )
        Busqueda.objects.create(
            usuario=self.user1,
            texto_problema='Query 2',
            categoria='Análisis de datos / predicción',
            fecha_creacion=yesterday
        )
        Busqueda.objects.create(
            usuario=self.user2,
            texto_problema='Query 3',
            categoria='Automatización',
            fecha_creacion=week_ago,
            resultado_llm='{"test": "result"}'
        )

    def test_panel_estadisticas_authenticated_superuser(self):
        """Test panel_estadisticas view for authenticated superuser"""
        response = self.client.get(reverse('dashboard:panel_estadisticas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/panel.html')

        # Check that context contains expected data
        self.assertIn('total_busquedas', response.context)
        self.assertIn('total_usuarios', response.context)
        self.assertIn('busquedas_activos', response.context)
        self.assertIn('busquedas_por_categoria', response.context)

        # Check values
        self.assertEqual(response.context['total_busquedas'], 3)
        self.assertEqual(response.context['total_usuarios'], 3)  # 2 users + superuser
        self.assertEqual(response.context['busquedas_activos'], 2)  # 2 users with busquedas

    def test_panel_estadisticas_data_accuracy(self):
        """Test that panel statistics are calculated correctly"""
        response = self.client.get(reverse('dashboard:panel_estadisticas'))

        # Check monthly statistics
        busquedas_mes = response.context['busquedas_mes']
        usuarios_mes = response.context['usuarios_mes']

        # Should include all 3 busquedas since they're recent
        self.assertGreaterEqual(busquedas_mes, 3)
        self.assertGreaterEqual(usuarios_mes, 2)

        # Check category distribution
        busquedas_por_categoria = response.context['busquedas_por_categoria']
        self.assertEqual(busquedas_por_categoria['automatizacion'], 2)
        self.assertEqual(busquedas_por_categoria['analisis_datos_prediccion'], 1)

    def test_panel_estadisticas_chart_data(self):
        """Test that chart data is properly formatted"""
        response = self.client.get(reverse('dashboard:panel_estadisticas'))

        # Check chart data exists and is JSON-serializable
        fechas_semanal = response.context['fechas_semanal']
        valores_semanal = response.context['valores_semanal']
        porcentaje_labels = response.context['porcentaje_labels']
        porcentaje_valores = response.context['porcentaje_valores']

        import json
        self.assertIsInstance(json.loads(fechas_semanal), list)
        self.assertIsInstance(json.loads(valores_semanal), list)
        self.assertIsInstance(json.loads(porcentaje_labels), list)
        self.assertIsInstance(json.loads(porcentaje_valores), list)

    def test_panel_estadisticas_display_names(self):
        """Test that display names are properly mapped"""
        response = self.client.get(reverse('dashboard:panel_estadisticas'))

        display_names = response.context['display_names']
        expected_names = {
            'automatizacion': 'Automatización',
            'analisis_datos_prediccion': 'Análisis de datos / predicción',
            'procesamiento_texto': 'Procesamiento de texto',
            'procesamiento_imagenes_video': 'Procesamiento de imágenes / video',
            'procesamiento_audio_voz': 'Procesamiento de audio / voz',
            'generacion_contenido': 'Generación de contenido',
            'recomendacion_personalizacion': 'Recomendación / personalización',
            'optimizacion_decision_inteligente': 'Optimización / decisión inteligente',
            'asistentes_conversacionales': 'Asistentes conversacionales'
        }

        for key, expected_name in expected_names.items():
            self.assertEqual(display_names[key], expected_name)

    def test_panel_estadisticas_scoring_data(self):
        """Test that scoring statistics are calculated correctly"""
        # Create a busqueda with resultado_llm for scoring
        mock_resultado = {
            "indices_clave": {
                "adecuacion_ia": {"puntuacion": 85},
                "factibilidad_tecnica": {"puntuacion": 90},
                "impacto_potencial": {"puntuacion": 80}
            }
        }

        busqueda = Busqueda.objects.create(
            usuario=self.user1,
            texto_problema='Scoring test query',
            categoria='Automatización',
            resultado_llm=str(mock_resultado).replace("'", '"')
        )

        response = self.client.get(reverse('dashboard:panel_estadisticas'))

        # Check that promedio_puntuacion is calculated
        promedio_puntuacion = response.context['promedio_puntuacion']
        self.assertIsInstance(promedio_puntuacion, float)

    def test_panel_estadisticas_not_superuser(self):
        """Test that regular users cannot access dashboard"""
        # Login as regular user
        self.client.logout()
        self.client.login(username='user1', password='pass123')

        response = self.client.get(reverse('dashboard:panel_estadisticas'))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_panel_estadisticas_not_authenticated(self):
        """Test that unauthenticated users are redirected"""
        self.client.logout()

        response = self.client.get(reverse('dashboard:panel_estadisticas'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_panel_estadisticas_empty_database(self):
        """Test panel with empty database"""
        # Clear all busquedas
        Busqueda.objects.all().delete()

        response = self.client.get(reverse('dashboard:panel_estadisticas'))
        self.assertEqual(response.status_code, 200)

        # Check that values are 0 or handle empty case
        self.assertEqual(response.context['total_busquedas'], 0)
        self.assertGreaterEqual(response.context['total_usuarios'], 1)  # At least superuser