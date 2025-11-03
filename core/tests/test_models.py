import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Busqueda


class BusquedaModelTest(TestCase):
    """Test suite for Busqueda model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_busqueda_creation(self):
        """Test Busqueda model creation"""
        busqueda = Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Test query for AI analysis',
            categoria='Automatización',
            resultado_llm='{"test": "result"}'
        )

        self.assertEqual(busqueda.usuario, self.user)
        self.assertEqual(busqueda.texto_problema, 'Test query for AI analysis')
        self.assertEqual(busqueda.categoria, 'Automatización')
        self.assertEqual(busqueda.resultado_llm, '{"test": "result"}')
        self.assertIsNotNone(busqueda.fecha_creacion)

    def test_busqueda_str_method(self):
        """Test Busqueda string representation"""
        busqueda = Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Test query',
            categoria='Automatización'
        )

        expected_str = f"Búsqueda de {self.user.username} - Test query..."
        self.assertEqual(str(busqueda), expected_str)

    def test_busqueda_categoria_choices(self):
        """Test that categoria field accepts valid choices"""
        valid_categorias = [
            'Automatización',
            'Análisis de datos / predicción',
            'Procesamiento de texto',
            'Procesamiento de imágenes / video',
            'Procesamiento de audio / voz',
            'Generación de contenido',
            'Recomendación / personalización',
            'Optimización / decisión inteligente',
            'Asistentes conversacionales'
        ]

        for categoria in valid_categorias:
            busqueda = Busqueda.objects.create(
                usuario=self.user,
                texto_problema=f'Test query for {categoria}',
                categoria=categoria
            )
            self.assertEqual(busqueda.categoria, categoria)

    def test_busqueda_blank_fields(self):
        """Test Busqueda with blank optional fields"""
        busqueda = Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Test query',
            categoria='Automatización'
        )

        self.assertIsNone(busqueda.resultado_llm)

    def test_busqueda_ordering(self):
        """Test that Busquedas are ordered by fecha_creacion descending"""
        # Force different timestamps by creating with a small delay
        import time
        busqueda1 = Busqueda.objects.create(
            usuario=self.user,
            texto_problema='First query',
            categoria='Automatización'
        )
        time.sleep(0.1)  # Small delay to ensure different timestamps
        busqueda2 = Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Second query',
            categoria='Automatización'
        )

        busquedas = Busqueda.objects.all()
        self.assertEqual(busquedas[0], busqueda2)  # Most recent first
        self.assertEqual(busquedas[1], busqueda1)  # Older second

    def test_busqueda_user_relationship(self):
        """Test foreign key relationship with User"""
        busqueda = Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Test query',
            categoria='Automatización'
        )

        # Test reverse relationship
        user_busquedas = self.user.busqueda_set.all()
        self.assertIn(busqueda, user_busquedas)

    def test_busqueda_long_consulta(self):
        """Test Busqueda with very long consulta"""
        long_consulta = 'A' * 1000  # Very long query
        busqueda = Busqueda.objects.create(
            usuario=self.user,
            texto_problema=long_consulta,
            categoria='Automatización'
        )

        self.assertEqual(busqueda.texto_problema, long_consulta)

    def test_busqueda_json_resultado(self):
        """Test Busqueda with complex JSON resultado_llm"""
        complex_json = {
            "indices_clave": {
                "adecuacion_ia": {"puntuacion": 85, "justificacion": "Excelente adecuación"},
                "factibilidad_tecnica": {"puntuacion": 90, "justificacion": "Factible técnicamente"},
                "impacto_potencial": {"puntuacion": 80, "justificacion": "Alto impacto"}
            },
            "recomendaciones": ["Implementar IA", "Capacitar equipo"],
            "riesgos": ["Dependencia tecnológica"]
        }

        import json
        busqueda = Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Complex analysis query',
            categoria='Análisis de datos / predicción',
            resultado_llm=complex_json
        )

        # Verify JSON can be parsed back
        import json
        parsed_result = json.loads(json.dumps(busqueda.resultado_llm))
        self.assertEqual(parsed_result['indices_clave']['adecuacion_ia']['puntuacion'], 85)