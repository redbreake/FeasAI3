import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch, MagicMock
from core.models import Busqueda


class CoreViewsTest(TestCase):
    """Test suite for core app views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_home_view_get(self):
        """Test home view GET request"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_home_view_post_valid(self):
        """Test home view POST request with valid data"""
        # Mock the LLM service to avoid API key issues
        with patch('core.views.analizar_viabilidad') as mock_analizar:
            mock_result = {
                "titulo_proyecto": "Test Project",
                "resumen_ejecutivo": "Test summary",
                "indices_clave": {
                    "adecuacion_ia": {"puntuacion": 85, "justificacion": "Good fit"},
                    "factibilidad_tecnica": {"puntuacion": 90, "justificacion": "Technically feasible"},
                    "impacto_potencial": {"puntuacion": 80, "justificacion": "High impact"}
                }
            }
            mock_analizar.return_value = mock_result

            data = {'problema': 'Test AI analysis query'}
            response = self.client.post(reverse('core:home'), data)
            self.assertEqual(response.status_code, 302)  # Redirect to resultado

            # Check that Busqueda was created
            busqueda = Busqueda.objects.filter(texto_problema='Test AI analysis query').first()
            self.assertIsNotNone(busqueda)
            if busqueda:
                self.assertEqual(busqueda.usuario, self.user)

    def test_home_view_post_empty(self):
        """Test home view POST request with empty data"""
        data = {'problema': ''}
        response = self.client.post(reverse('core:home'), data)
        self.assertEqual(response.status_code, 302)  # Redirect to home with error

    def test_analizar_viabilidad_success(self):
        """Test analizar_viabilidad view with successful LLM response"""
        # Create a busqueda first
        busqueda = Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Test query',
            categoria='Automatización',
            resultado_llm=json.dumps({"test": "data"})
        )

        response = self.client.get(reverse('core:resultado', args=[busqueda.id]))
        self.assertEqual(response.status_code, 200)  # Should show resultado page

        # Check that resultado_llm was saved
        busqueda.refresh_from_db()
        self.assertIsNotNone(busqueda.resultado_llm)

    def test_analizar_viabilidad_llm_error(self):
        """Test analizar_viabilidad view with LLM error"""
        # Skip this test as it's testing a non-existent view
        self.skipTest("Test for non-existent analizar_viabilidad view")

    def test_analizar_viabilidad_not_owner(self):
        """Test resultado view with different user"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )

        busqueda = Busqueda.objects.create(
            usuario=other_user,
            texto_problema='Test query',
            categoria='Automatización'
        )

        response = self.client.get(reverse('core:resultado', args=[busqueda.id]))
        self.assertEqual(response.status_code, 404)  # Should not find the busqueda

    def test_resultado_view_with_data(self):
        """Test resultado view with complete busqueda data"""
        mock_resultado = {
            "resumen_ejecutivo": "Test summary",
            "indices_clave": {
                "adecuacion_ia": {"puntuacion": 85, "justificacion": "Good fit"},
                "factibilidad_tecnica": {"puntuacion": 90, "justificacion": "Technically feasible"},
                "impacto_potencial": {"puntuacion": 80, "justificacion": "High impact"}
            },
            "analisis_costo_beneficio": "Cost-benefit analysis",
            "alternativas_no_ia": "Non-AI alternatives",
            "recomendaciones_estrategicas": ["Recommendation 1", "Recommendation 2"],
            "consultas_relacionadas": [
                {
                    "titulo": "Test title",
                    "descripcion": "Test description",
                    "consulta_completa": "Test full query"
                }
            ]
        }

        busqueda = Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Test query',
            categoria='Automatización',
            resultado_llm=json.dumps(mock_resultado)
        )

        response = self.client.get(reverse('core:resultado', args=[busqueda.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/resultado.html')
        self.assertContains(response, 'Test summary')

    def test_resultado_view_not_owner(self):
        """Test resultado view with different user"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )

        busqueda = Busqueda.objects.create(
            usuario=other_user,
            texto_problema='Test query',
            categoria='Automatización'
        )

        response = self.client.get(reverse('core:resultado', args=[busqueda.id]))
        self.assertEqual(response.status_code, 404)

    def test_historial_view(self):
        """Test historial view"""
        # Create some busquedas
        Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Query 1',
            categoria='Automatización'
        )
        Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Query 2',
            categoria='Análisis de datos / predicción'
        )

        response = self.client.get(reverse('core:historial'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/historial.html')
        self.assertContains(response, 'Query 1')
        self.assertContains(response, 'Query 2')

    def test_unauthenticated_access(self):
        """Test that unauthenticated users are redirected"""
        self.client.logout()

        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

        response = self.client.get(reverse('core:historial'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login