import pytest
from django.test import TestCase
from core.utils import (
    validar_categoria,
    formatear_fecha,
    calcular_promedio_puntuaciones,
    sanitizar_texto
)


class UtilsTest(TestCase):
    """Test suite for core utils functions"""

    def test_validar_categoria_valid(self):
        """Test validar_categoria with valid categories"""
        valid_categories = [
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

        for categoria in valid_categories:
            self.assertTrue(validar_categoria(categoria))

    def test_validar_categoria_invalid(self):
        """Test validar_categoria with invalid categories"""
        invalid_categories = [
            'Categoría inválida',
            'Otra categoría',
            '',
            None,
            'automatización'  # Should be case sensitive
        ]

        for categoria in invalid_categories:
            self.assertFalse(validar_categoria(categoria))

    def test_formatear_fecha(self):
        """Test formatear_fecha function"""
        from datetime import datetime

        fecha = datetime(2024, 1, 15, 10, 30, 45)
        resultado = formatear_fecha(fecha)

        self.assertEqual(resultado, '15/01/2024 10:30:45')

    def test_formatear_fecha_none(self):
        """Test formatear_fecha with None input"""
        resultado = formatear_fecha(None)
        self.assertEqual(resultado, '')

    def test_calcular_promedio_puntuaciones_complete(self):
        """Test calcular_promedio_puntuaciones with complete data"""
        puntuaciones = [80, 90, 70, 85, 95]
        promedio = calcular_promedio_puntuaciones(puntuaciones)

        self.assertAlmostEqual(promedio, 84.0)

    def test_calcular_promedio_puntuaciones_empty(self):
        """Test calcular_promedio_puntuaciones with empty list"""
        puntuaciones = []
        promedio = calcular_promedio_puntuaciones(puntuaciones)

        self.assertEqual(promedio, 0.0)

    def test_calcular_promedio_puntuaciones_none_values(self):
        """Test calcular_promedio_puntuaciones with None values"""
        puntuaciones = [80, None, 70, None, 90]
        promedio = calcular_promedio_puntuaciones(puntuaciones)

        # Should calculate average of non-None values
        expected = (80 + 70 + 90) / 3
        self.assertAlmostEqual(promedio, expected)

    def test_sanitizar_texto_basic(self):
        """Test sanitizar_texto with basic input"""
        texto = "Hola mundo"
        resultado = sanitizar_texto(texto)

        self.assertEqual(resultado, "Hola mundo")

    def test_sanitizar_texto_with_html(self):
        """Test sanitizar_texto with HTML tags"""
        texto = "<script>alert('hack')</script>Hola <b>mundo</b>"
        resultado = sanitizar_texto(texto)

        # Should remove HTML tags
        self.assertNotIn('<script>', resultado)
        self.assertNotIn('<b>', resultado)
        self.assertIn('Hola', resultado)
        self.assertIn('mundo', resultado)

    def test_sanitizar_texto_with_special_chars(self):
        """Test sanitizar_texto with special characters"""
        texto = "Hola@mundo#especial&caracteres"
        resultado = sanitizar_texto(texto)

        # Should keep most characters but may sanitize some
        self.assertIn('Hola', resultado)
        self.assertIn('mundo', resultado)

    def test_sanitizar_texto_empty(self):
        """Test sanitizar_texto with empty input"""
        resultado = sanitizar_texto("")
        self.assertEqual(resultado, "")

    def test_sanitizar_texto_none(self):
        """Test sanitizar_texto with None input"""
        resultado = sanitizar_texto(None)
        self.assertEqual(resultado, "")

    def test_validar_categoria_edge_cases(self):
        """Test validar_categoria with edge cases"""
        # Test with extra whitespace
        self.assertFalse(validar_categoria(' Automatización '))
        self.assertFalse(validar_categoria('Automatización '))

        # Test with similar but different names
        self.assertFalse(validar_categoria('Automatizacion'))  # Missing accent
        self.assertFalse(validar_categoria('automatización'))  # Lowercase

    def test_formatear_fecha_different_formats(self):
        """Test formatear_fecha with different datetime objects"""
        from datetime import date, time

        # Test with date only
        fecha_date = date(2024, 1, 15)
        with self.assertRaises(AttributeError):
            formatear_fecha(fecha_date)  # Should handle gracefully or raise error

    def test_calcular_promedio_puntuaciones_single_value(self):
        """Test calcular_promedio_puntuaciones with single value"""
        puntuaciones = [85]
        promedio = calcular_promedio_puntuaciones(puntuaciones)

        self.assertEqual(promedio, 85.0)

    def test_calcular_promedio_puntuaciones_all_none(self):
        """Test calcular_promedio_puntuaciones with all None values"""
        puntuaciones = [None, None, None]
        promedio = calcular_promedio_puntuaciones(puntuaciones)

        self.assertEqual(promedio, 0.0)

    def test_sanitizar_texto_sql_injection(self):
        """Test sanitizar_texto against potential SQL injection"""
        texto = "'; DROP TABLE users; --"
        resultado = sanitizar_texto(texto)

        # Should not contain dangerous SQL
        self.assertNotIn('DROP', resultado.upper())
        self.assertNotIn('TABLE', resultado.upper())