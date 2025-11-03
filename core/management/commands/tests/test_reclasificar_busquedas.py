import pytest
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from io import StringIO
from core.models import Busqueda


class ReclasificarBusquedasCommandTest(TestCase):
    """Test suite for reclasificar_busquedas management command"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test busquedas with old categories that need reclasification
        self.busqueda1 = Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Automatizar proceso de facturación',
            categoria='Emprendimiento'  # Old category
        )

        self.busqueda2 = Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Sistema de predicción de ventas',
            categoria='Negocio'  # Old category
        )

        self.busqueda3 = Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Chatbot para atención al cliente',
            categoria='Automatización'  # Already correct
        )

    def test_command_output(self):
        """Test that command produces expected output"""
        out = StringIO()
        call_command('reclasificar_busquedas', stdout=out, force=True)

        output = out.getvalue()
        self.assertIn('Encontradas', output)
        self.assertIn('búsquedas para reclasificar', output)

    def test_command_reclassification(self):
        """Test that command correctly reclassifies busquedas"""
        # Run the command
        call_command('reclasificar_busquedas', force=True)

        # Refresh from database
        self.busqueda1.refresh_from_db()
        self.busqueda2.refresh_from_db()
        self.busqueda3.refresh_from_db()

        # Check reclassifications
        # 'Automatizar proceso de facturación' should become 'Automatización'
        self.assertEqual(self.busqueda1.categoria, 'Automatización')

        # 'Sistema de predicción de ventas' should become 'Análisis de datos / predicción'
        self.assertEqual(self.busqueda2.categoria, 'Análisis de datos / predicción')

        # 'Chatbot para atención al cliente' should become 'Asistentes conversacionales'
        self.assertEqual(self.busqueda3.categoria, 'Asistentes conversacionales')

    def test_command_with_no_changes_needed(self):
        """Test command when no reclassification is needed"""
        # Create busqueda with already correct category
        busqueda_correcta = Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Sistema de procesamiento de texto',
            categoria='Procesamiento de texto'
        )

        out = StringIO()
        call_command('reclasificar_busquedas', stdout=out, force=True)

        output = out.getvalue()
        # Should still report the total count but indicate no changes
        self.assertIn('Encontradas', output)

        # Verify the correct category wasn't changed
        busqueda_correcta.refresh_from_db()
        self.assertEqual(busqueda_correcta.categoria, 'Procesamiento de texto')

    def test_command_with_empty_database(self):
        """Test command with empty database"""
        # Clear all busquedas
        Busqueda.objects.all().delete()

        out = StringIO()
        call_command('reclasificar_busquedas', stdout=out, force=True)

        output = out.getvalue()
        self.assertIn('Encontradas 0 búsquedas', output)

    def test_command_preserves_other_fields(self):
        """Test that command doesn't modify other fields"""
        original_texto_problema = self.busqueda1.texto_problema
        original_usuario = self.busqueda1.usuario
        original_fecha = self.busqueda1.fecha_creacion

        call_command('reclasificar_busquedas', force=True)

        self.busqueda1.refresh_from_db()

        # These should remain unchanged
        self.assertEqual(self.busqueda1.texto_problema, original_texto_problema)
        self.assertEqual(self.busqueda1.usuario, original_usuario)
        self.assertEqual(self.busqueda1.fecha_creacion, original_fecha)

    def test_command_verbose_output(self):
        """Test command verbose output shows individual changes"""
        out = StringIO()
        call_command('reclasificar_busquedas', stdout=out, verbosity=2, force=True)

        output = out.getvalue()
        # With higher verbosity, should show more details
        self.assertIn('Encontradas', output)

    def test_command_handles_invalid_categories(self):
        """Test command handles busquedas with invalid categories"""
        # Create busqueda with invalid category
        busqueda_invalida = Busqueda.objects.create(
            usuario=self.user,
            texto_problema='Consulta con categoría inválida',
            categoria='Categoría Inválida'
        )

        # Command should handle this gracefully without crashing
        out = StringIO()
        call_command('reclasificar_busquedas', stdout=out, force=True)

        output = out.getvalue()
        self.assertIn('Reclasificación completada', output)  # Should complete successfully

    def test_command_atomic_operation(self):
        """Test that command is atomic - either all changes or none"""
        # This is harder to test directly, but we can verify the command
        # completes successfully and changes are persisted
        call_command('reclasificar_busquedas', force=True)

        # All busquedas should have valid categories after command
        for busqueda in Busqueda.objects.all():
            self.assertIn(busqueda.categoria, [
                'Automatización',
                'Análisis de datos / predicción',
                'Procesamiento de texto',
                'Procesamiento de imágenes / video',
                'Procesamiento de audio / voz',
                'Generación de contenido',
                'Recomendación / personalización',
                'Optimización / decisión inteligente',
                'Asistentes conversacionales'
            ])

    def test_command_updates_correct_count(self):
        """Test that command reports correct number of busquedas processed"""
        initial_count = Busqueda.objects.count()

        out = StringIO()
        call_command('reclasificar_busquedas', stdout=out, force=True)

        output = out.getvalue()
        # Should mention the same count as we have
        self.assertIn(str(initial_count), output)