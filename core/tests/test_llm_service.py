import pytest
import json
from django.test import TestCase
from unittest.mock import patch, MagicMock, mock_open
from core.llm_service import (
    analizar_viabilidad_con_gemini,
    analizar_viabilidad_con_cerebras,
    analizar_viabilidad,
    disenar_prompt_robusto
)


class LLMServiceTest(TestCase):
    """Test suite for LLM service functions"""

    def setUp(self):
        """Set up test data"""
        self.test_problema = "Implementar un sistema de IA para automatizar el procesamiento de facturas"

    @patch('core.llm_service.genai.GenerativeModel')
    def test_analizar_viabilidad_con_gemini_success(self, mock_model_class):
        """Test analizar_viabilidad_con_gemini with successful response"""
        # Mock the model and response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '''{
            "titulo_proyecto": "Test title",
            "resumen_ejecutivo": "Test summary",
            "veredicto_ia": "Ideal para IA",
            "indices_clave": {
                "adecuacion_ia": {"puntuacion": 85, "justificacion": "Good fit"},
                "factibilidad_tecnica": {"puntuacion": 90, "justificacion": "Technically feasible"},
                "impacto_potencial": {"puntuacion": 80, "justificacion": "High impact"}
            },
            "analisis_detallado": {
                "justificacion_ia": "AI justification",
                "requisitos_y_desafios_tecnicos": "Technical requirements",
                "analisis_coste_beneficio": "Cost-benefit analysis",
                "alternativas_no_ia": "Non-AI alternatives"
            },
            "recomendaciones_estrategicas": ["Recommendation 1", "Recommendation 2"],
            "consultas_relacionadas": [
                {
                    "titulo": "Test title",
                    "descripcion": "Test description",
                    "consulta_completa": "Test full query"
                }
            ],
            "datos_grafico_radar": {
                "labels": ["Adecuación", "Factibilidad", "Impacto", "Competitiva", "Complejidad"],
                "valoracion": [8, 9, 8, 7, 6]
            }
        }'''

        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        result = analizar_viabilidad_con_gemini(self.test_problema)

        # The mock returns the JSON string as text, so the function parses it
        # The mock response.text is the JSON string, so json.loads will parse it correctly
        self.assertIsInstance(result, dict)
        # Check that the function returned the parsed JSON from the mock
        self.assertEqual(result['titulo_proyecto'], 'Test title')
        self.assertEqual(result['resumen_ejecutivo'], 'Test summary')
        self.assertIn('indices_clave', result)
        self.assertIn('consultas_relacionadas', result)

    @patch('core.llm_service.genai.GenerativeModel')
    def test_analizar_viabilidad_con_gemini_api_error(self, mock_model_class):
        """Test analizar_viabilidad_con_gemini with API error"""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model

        result = analizar_viabilidad_con_gemini(self.test_problema)
        self.assertIn("error", result)
        self.assertIn("No se pudo obtener una respuesta del modelo de IA", result["error"])

    @patch('core.llm_service.genai.GenerativeModel')
    def test_analizar_viabilidad_con_gemini_invalid_json(self, mock_model_class):
        """Test analizar_viabilidad_con_gemini with invalid JSON response"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Invalid JSON response"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        result = analizar_viabilidad_con_gemini(self.test_problema)
        self.assertIn("error", result)
        self.assertIn("La respuesta del modelo no es un JSON válido", result["error"])

    def test_disenar_prompt_robusto(self):
        """Test disenar_prompt_robusto function"""
        prompt = disenar_prompt_robusto(self.test_problema)

        self.assertIsInstance(prompt, str)
        self.assertIn(self.test_problema, prompt)
        self.assertIn("JSON", prompt)
        self.assertIn("resumen_ejecutivo", prompt)
        self.assertIn("consultas_relacionadas", prompt)

        # Check that it includes all required fields
        required_fields = [
            "resumen_ejecutivo",
            "indices_clave",
            "adecuacion_ia",
            "factibilidad_tecnica",
            "impacto_potencial",
            "analisis_coste_beneficio",
            "alternativas_no_ia",
            "recomendaciones_estrategicas",
            "consultas_relacionadas"
        ]

        for field in required_fields:
            self.assertIn(field, prompt)

    def test_analizar_viabilidad_gemini_missing_api_key(self):
        """Test analizar_viabilidad_con_gemini with missing API key"""
        import os
        original_key = os.environ.get("GEMINI_API_KEY")
        try:
            os.environ.pop("GEMINI_API_KEY", None)
            result = analizar_viabilidad_con_gemini(self.test_problema)
            self.assertIn("error", result)
            self.assertIn("API Key de Gemini no configurada", result["error"])
        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key

    def test_analizar_viabilidad_cerebras_missing_api_key(self):
        """Test analizar_viabilidad_con_cerebras with missing API key"""
        import os
        original_key = os.environ.get("CEREBRAS_API_KEY")
        try:
            os.environ.pop("CEREBRAS_API_KEY", None)
            result = analizar_viabilidad_con_cerebras(self.test_problema)
            self.assertIn("error", result)
            self.assertIn("API Key de Cerebras no configurada", result["error"])
        finally:
            if original_key:
                os.environ["CEREBRAS_API_KEY"] = original_key

    def test_analizar_viabilidad_invalid_model(self):
        """Test analizar_viabilidad with invalid model"""
        result = analizar_viabilidad("invalid_model", self.test_problema)
        self.assertIn("error", result)
        self.assertIn("Modelo no soportado", result["error"])

    def test_analizar_viabilidad_gemini_success(self):
        """Test analizar_viabilidad with gemini model"""
        with patch('core.llm_service.analizar_viabilidad_con_gemini') as mock_func:
            mock_func.return_value = {"titulo_proyecto": "Test"}
            result = analizar_viabilidad('gemini', self.test_problema)
            mock_func.assert_called_once_with(self.test_problema)
            self.assertEqual(result["titulo_proyecto"], "Test")

    def test_analizar_viabilidad_cerebras_success(self):
        """Test analizar_viabilidad with cerebras model"""
        with patch('core.llm_service.analizar_viabilidad_con_cerebras') as mock_func:
            mock_func.return_value = {"titulo_proyecto": "Test"}
            result = analizar_viabilidad('cerebras', self.test_problema)
            mock_func.assert_called_once_with(self.test_problema)
            self.assertEqual(result["titulo_proyecto"], "Test")

    @patch('core.llm_service.genai.GenerativeModel')
    def test_analizar_viabilidad_con_gemini_empty_response(self, mock_model_class):
        """Test analizar_viabilidad_con_gemini with empty response"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = ""
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        result = analizar_viabilidad_con_gemini(self.test_problema)
        self.assertIn("error", result)
        self.assertIn("La respuesta del modelo no es un JSON válido", result["error"])

    @patch('core.llm_service.genai.GenerativeModel')
    def test_analizar_viabilidad_con_gemini_partial_json(self, mock_model_class):
        """Test analizar_viabilidad_con_gemini with partial JSON response"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"titulo_proyecto": "Test", "resumen_ejecutivo":'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        result = analizar_viabilidad_con_gemini(self.test_problema)
        self.assertIn("error", result)
        self.assertIn("La respuesta del modelo no es un JSON válido", result["error"])

    def test_disenar_prompt_robusto_includes_problem_context(self):
        """Test that the prompt includes the problem context"""
        prompt = disenar_prompt_robusto(self.test_problema)

        # Check that the problem is referenced in the prompt
        self.assertIn("Implementar un sistema de IA", prompt)
        self.assertIn("facturas", prompt)

    def test_disenar_prompt_robusto_json_structure(self):
        """Test that the prompt requests proper JSON structure"""
        prompt = disenar_prompt_robusto(self.test_problema)

        # Should request valid JSON
        self.assertIn('"titulo_proyecto"', prompt)
        self.assertIn("resumen_ejecutivo", prompt)
        self.assertIn("consultas_relacionadas", prompt)

        # Should specify array structure for consultas_relacionadas
        self.assertIn('"titulo"', prompt)
        self.assertIn('"descripcion"', prompt)
        self.assertIn('"consulta_completa"', prompt)