"""
Módulo de servicios de IA para el análisis de viabilidad de proyectos.

Este archivo contiene las funciones necesarias para interactuar con modelos de IA
como Cerebras y Gemini, generando análisis críticos sobre la aplicabilidad de
la inteligencia artificial en diferentes proyectos o problemas de negocio.
El enfoque es ser pragmático y realista, evaluando no solo las posibilidades
técnicas sino también los costos, datos requeridos y alternativas tradicionales.
"""

import os  # Para acceder a variables de entorno del sistema
import json  # Para manejar datos en formato JSON, clave para las respuestas de los modelos
from cerebras.cloud.sdk import Cerebras  # Cliente oficial para la API de Cerebras
import google.generativeai as genai  # Biblioteca para interactuar con modelos de Google Gemini
from google.generativeai import types  # Necesario para configurar la generación de respuestas

# Configuración inicial para Cerebras: obtenemos la clave API desde las variables de entorno
# Esta clave es esencial para autenticar las llamadas a la API de Cerebras
CEREBRAS_API_KEY = os.environ.get("CEREBRAS_API_KEY")
if not CEREBRAS_API_KEY:
    # Si no está configurada, mostramos una advertencia pero no detenemos la ejecución
    # Esto permite que otros modelos funcionen aunque Cerebras no esté disponible
    print("Advertencia: La variable de entorno CEREBRAS_API_KEY no está configurada.")


def disenar_prompt_robusto(problema_del_usuario: str) -> str:
    """
    Diseña un prompt sofisticado y crítico para que los modelos de IA analicen
    la viabilidad de aplicar inteligencia artificial a un problema específico.

    Este prompt está diseñado para obtener análisis realistas y pragmáticos,
    enfocándose en costos, datos y alternativas, en lugar de ser excesivamente
    optimista como lo hacen muchos análisis de IA.

    Parámetros:
        problema_del_usuario: La descripción del problema o proyecto que se quiere analizar

    Retorna:
        Un string con el prompt completo en español, listo para enviar a un modelo de IA
    """
    # Validación exhaustiva del input para evitar errores posteriores
    # Es crítico validar aquí porque los modelos de IA pueden fallar de formas extrañas con inputs inválidos
    # print(f"Debug: problema_del_usuario recibido: '{problema_del_usuario}' (tipo: {type(problema_del_usuario)})")

    if problema_del_usuario is None:
        print("Error: problema_del_usuario es None")
        return None

    if not isinstance(problema_del_usuario, str):
        print(f"Error: problema_del_usuario no es string, es {type(problema_del_usuario)}")
        return None

    problema_stripped = problema_del_usuario.strip()
    if not problema_stripped:
        print("Error: problema_del_usuario está vacío después de strip")
        return None

    if len(problema_stripped) < 10:
        print(f"Error: problema_del_usuario es demasiado corto: {len(problema_stripped)} caracteres")
        return None

    # Construcción del prompt principal con instrucciones detalladas
    # Este prompt está diseñado específicamente para obtener análisis críticos y realistas
    # La instrucción de ser "crítico y pragmático" es fundamental para evitar el sesgo optimista común en análisis de IA
    prompt = f"""ACTÚA COMO UN CONSULTOR SENIOR DE IA, PRAGMÁTICO Y CRÍTICO.
Tu objetivo principal no es ser optimista, sino realista. Analiza los costos, los requisitos de datos y las alternativas no-IA. Tu reputación depende de evitar que los clientes inviertan en proyectos de IA inviables.
La respuesta DEBE SER ÚNICAMENTE un objeto JSON válido, sin ningún texto o explicación fuera del propio JSON.

PROBLEMA O PROYECTO A ANALIZAR: {problema_stripped}

El objeto JSON de salida debe seguir estrictamente la siguiente estructura:

{{
  "titulo_proyecto": "Un título corto y descriptivo para la idea.",
  "resumen_ejecutivo": "Un párrafo de 2-4 frases resumiendo el análisis, incluyendo el veredicto final y la principal justificación.",
  "veredicto_ia": "Clasifica la idea en UNA de las siguientes categorías: 'Ideal para IA', 'Prometedor con Desafíos', 'Poco Práctico' o 'Inapropiado para IA'.",

  "indices_clave": {{
    "adecuacion_ia": {{
      "puntuacion": Un número entero del 1 al 100,
      "justificacion": "Breve explicación sobre si el problema se alinea con las capacidades de la IA (predicción, clasificación, generación, etc.)."
    }},
    "factibilidad_tecnica": {{
      "puntuacion": Un número entero del 1 al 100,
      "justificacion": "Análisis sobre la disponibilidad y calidad de los datos, y la complejidad tecnológica."
    }},
    "impacto_potencial": {{
      "puntuacion": Un número entero del 1 al 100,
      "justificacion": "Evaluación del posible retorno de la inversión (ROI), eficiencia ganada o ventaja competitiva."
    }}
  }},

  "analisis_detallado": {{
    "justificacion_ia": "Explica en detalle por qué la IA es (o no es) la herramienta adecuada, mencionando tipos de modelos o técnicas aplicables (ej. NLP, Computer Vision, Modelos Predictivos).",
    "requisitos_y_desafios_tecnicos": "Describe los datos necesarios (volumen, calidad, etiquetado), la infraestructura requerida y los principales obstáculos técnicos.",
    "analisis_coste_beneficio": "Una evaluación cualitativa de los costos estimados (desarrollo, datos, mantenimiento) frente a los beneficios potenciales.",
    "alternativas_no_ia": "Sugiere 1 o 2 soluciones más simples que no involucren IA y que podrían resolver una parte o la totalidad del problema de forma más eficiente."
  }},

  "recomendaciones_estrategicas": [
    "Una lista de 3 a 5 pasos concretos y accionables. Si el proyecto es viable, los pasos para iniciarlo. Si no lo es, los pasos para redefinirlo o buscar alternativas."
  ],

  "consultas_relacionadas": [
    {{
      "titulo": "Análisis de Aspectos Técnicos Avanzados",
      "descripcion": "Explora en detalle los requerimientos técnicos específicos, infraestructura necesaria y posibles desafíos de implementación para este proyecto de IA.",
      "consulta_completa": "Basado en el análisis anterior sobre '{problema_del_usuario}', profundiza en los aspectos técnicos: ¿qué tipo de modelos de IA serían más apropiados? ¿Qué volumen y calidad de datos se necesitan? ¿Qué infraestructura computacional requeriría? ¿Cuáles son los principales cuellos de botella técnicos y cómo superarlos?"
    }},
    {{
      "titulo": "Evaluación Financiera y ROI Detallado",
      "descripcion": "Realiza un análisis financiero completo incluyendo costos de desarrollo, mantenimiento, retorno de inversión esperado y comparación con alternativas tradicionales.",
      "consulta_completa": "Continuando con el proyecto '{problema_del_usuario}' analizado anteriormente, realiza una evaluación financiera detallada: calcula los costos estimados de desarrollo e implementación, estima los ahorros o ingresos adicionales generados, calcula el período de retorno de inversión, y compara con soluciones convencionales no basadas en IA."
    }},
    {{
      "titulo": "Estrategia de Implementación Paso a Paso",
      "descripcion": "Desarrolla un plan de implementación práctico con timeline, recursos necesarios y métricas de éxito para llevar este proyecto de IA a producción.",
      "consulta_completa": "Para el proyecto '{problema_del_usuario}' que hemos evaluado, crea una estrategia de implementación detallada: define las fases del proyecto con timelines realistas, identifica los recursos humanos y tecnológicos necesarios, establece métricas de éxito cuantificables, y describe cómo medir y validar los resultados en cada etapa."
    }}
  ],

  "datos_grafico_radar": {{
    "labels": ["Adecuación del Problema", "Factibilidad de Datos", "Impacto/ROI", "Ventaja Competitiva", "Complejidad Técnica"],
    "valoracion": [
      Un entero del 1 al 10 para Adecuación del Problema a la IA,
      Un entero del 1 al 10 para la calidad y disponibilidad de Datos,
      Un entero del 1 al 10 para el Retorno de Inversión potencial,
      Un entero del 1 al 10 para la Ventaja Competitiva que genera,
      Un entero del 1 al 10 para la Complejidad Técnica (donde 1 es extremadamente complejo y 10 es simple)
    ]
  }}
}}
    """
    return prompt


def analizar_viabilidad_con_cerebras(problema_usuario: str) -> dict:
    """
    Función principal para interactuar con la API de Cerebras.

    Esta función maneja todo el proceso de comunicación con el modelo Cerebras,
    incluyendo la generación del prompt, el envío de la solicitud, el procesamiento
    de la respuesta y la extracción del JSON estructurado. Incluye validaciones
    exhaustivas en cada paso para garantizar robustez.

    Parámetros:
        problema_usuario: Descripción del problema o proyecto a analizar

    Retorna:
        Diccionario con el análisis completo o un diccionario con clave "error" si falla
    """
    # Verificación inicial de configuración antes de proceder
    if not CEREBRAS_API_KEY:
        return {"error": "API Key de Cerebras no configurada en el servidor."}

    try:
        # Inicialización del cliente de Cerebras con la clave API
        client = Cerebras(api_key=CEREBRAS_API_KEY)

        # Generación del prompt personalizado para este problema específico
        prompt_final = disenar_prompt_robusto(problema_usuario)

        # Validación crítica del prompt generado - no podemos enviar algo inválido
        if prompt_final is None:
            print("Error: disenar_prompt_robusto devolvió None")
            return {"error": "Error interno al generar el prompt de análisis."}

        if not isinstance(prompt_final, str) or prompt_final.strip() == "":
            print(f"Error: prompt_final no es string válido: {type(prompt_final)}")
            return {"error": "Error interno al generar el prompt de análisis."}

        # Logging para debugging - útil para ver qué se está enviando
        print(f"Prompt final antes de enviar: '{prompt_final[:500]}...'")
        print(f"Longitud del prompt: {len(prompt_final)}")

        # Preparación del contenido para el mensaje
        # En teoría siempre debería ser string, pero esta validación añade robustez
        if isinstance(prompt_final, str):
            content = prompt_final
        else:
            # Fallback por si acaso, aunque es muy improbable
            content = str(prompt_final)

        messages = [{"role": "user", "content": content}]
        print(f"Content a enviar: '{content[:500]}...'")

        # Envío de la solicitud a la API de Cerebras
        # Usamos el modelo Qwen instruct que es bueno para análisis estructurado
        response = client.chat.completions.create(
            model="qwen-3-235b-a22b-instruct-2507",  # Modelo específico de Cerebras para tareas instructivas
            messages=messages,  # Contiene el prompt como mensaje del usuario
            max_tokens=20000,  # Límite alto para respuestas detalladas
            temperature=0.7,   # Balance entre creatividad y consistencia
            top_p=0.8,         # Sampling nucleus para diversidad controlada
            stream=False       # Respuesta completa, no streaming
        )

        # Validación exhaustiva de la respuesta - las APIs pueden fallar de formas inesperadas
        print(f"Tipo de response: {type(response)}")
        print(f"Response tiene atributo choices: {hasattr(response, 'choices')}")

        if not response:
            print("Respuesta de Cerebras es None")
            print(f"Tipo esperado de response: {type(response)}")
            return {"error": "La API de Cerebras no devolvió una respuesta válida."}

        if not hasattr(response, 'choices'):
            print("Respuesta de Cerebras no tiene atributo 'choices'")
            print(f"Atributos disponibles: {[attr for attr in dir(response) if not attr.startswith('_')]}")
            return {"error": "La respuesta de Cerebras no tiene la estructura esperada (falta choices)."}

        if not response.choices:
            print("Respuesta de Cerebras tiene choices vacío")
            print(f"Response completo: {response}")
            return {"error": "La respuesta de Cerebras no contiene opciones válidas."}

        print(f"Número de choices: {len(response.choices)}")

        first_choice = response.choices[0]
        print(f"Tipo de first_choice: {type(first_choice)}")
        print(f"First_choice es None: {first_choice is None}")

        if first_choice is None:
            print("La primera choice es None")
            return {"error": "La primera opción de respuesta de Cerebras es None."}

        if not hasattr(first_choice, 'message'):
            print("First_choice no tiene atributo 'message'")
            print(f"Atributos de first_choice: {[attr for attr in dir(first_choice) if not attr.startswith('_')]}")
            return {"error": "La respuesta de Cerebras no contiene un mensaje válido."}

        message = first_choice.message
        print(f"Tipo de message: {type(message)}")
        print(f"Message es None: {message is None}")

        if message is None:
            print("El message es None")
            return {"error": "El mensaje de respuesta de Cerebras es None."}

        if not hasattr(message, 'content'):
            print("Message no tiene atributo 'content'")
            print(f"Atributos de message: {[attr for attr in dir(message) if not attr.startswith('_')]}")
            return {"error": "El mensaje de Cerebras no contiene contenido."}

        # Extraemos y analizamos el contenido de la respuesta - paso crítico
        raw_content = message.content
        print(f"Respuesta cruda de Cerebras: '{raw_content}'")
        print(f"Tipo de respuesta: {type(raw_content)}")
        print(f"Longitud de la respuesta: {len(raw_content) if raw_content else 0}")
        print(f"Primeros 200 caracteres: '{raw_content[:200] if raw_content else 'None'}'")
        print(f"Últimos 200 caracteres: '{raw_content[-200:] if raw_content else 'None'}'")
        print(f"Contiene '{{' : {'{{' in raw_content if raw_content else False}")
        print(f"Contiene '}}' : {'}}' in raw_content if raw_content else False}")

        # Verificaciones finales antes de procesar el JSON
        if raw_content is None:
            print("La respuesta de Cerebras es None")
            return {"error": "La respuesta del modelo es None. Verifica la configuración de la API o intenta nuevamente."}

        if not isinstance(raw_content, str) or raw_content.strip() == "":
            print(f"La respuesta de Cerebras está vacía o no es string: {type(raw_content)}")
            return {"error": "La respuesta del modelo está vacía. Intente nuevamente con una consulta más específica."}

        # Función especializada para extraer JSON válido de respuestas de modelos de IA
        # Los modelos pueden devolver texto adicional o JSON malformado
        def extraer_json_de_respuesta(texto):
            import re
            # Estrategia de extracción robusta: múltiples intentos para encontrar JSON válido
            texto = texto.strip()

            # Primer intento: si el texto completo ya es JSON válido
            try:
                return json.loads(texto)
            except json.JSONDecodeError:
                pass

            # Segundo intento: buscar patrones JSON con expresiones regulares
            json_objects = re.findall(r'\{.*\}', texto, re.DOTALL)

            for obj in json_objects:
                try:
                    balanced = balancear_llaves(obj)
                    if balanced:
                        return json.loads(balanced)
                except json.JSONDecodeError:
                    continue

            # Tercer intento: extracción manual balanceando llaves
            start = texto.find('{')
            if start == -1:
                return None

            brace_count = 0
            end = start
            for i, char in enumerate(texto[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i
                        break

            if brace_count == 0 and end > start:
                json_candidate = texto[start:end+1]
                try:
                    return json.loads(json_candidate)
                except json.JSONDecodeError:
                    pass

            return None

        # Función auxiliar para balancear llaves en JSON
        def balancear_llaves(texto):
            brace_count = 0
            start = texto.find('{')
            if start == -1:
                return None

            for i in range(start, len(texto)):
                if texto[i] == '{':
                    brace_count += 1
                elif texto[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return texto[start:i+1]
            return None

        # Último paso: extraer el JSON estructurado de la respuesta del modelo
        resultado_dict = extraer_json_de_respuesta(raw_content)

        if resultado_dict is None:
            print(f"No se pudo extraer JSON válido de: '{raw_content}'")
            return {"error": "La respuesta del modelo no contiene un JSON válido. El modelo puede no estar siguiendo las instrucciones correctamente."}

        return resultado_dict

    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON de la API de Cerebras: {e}")
        return {"error": f"La respuesta del modelo no es un JSON válido. Detalles: {str(e)}"}
    except Exception as e:
        print(f"Error al llamar a la API de Cerebras o al procesar su respuesta: {e}")
        print(f"Tipo de excepción: {type(e)}")
        import traceback
        print("Traceback completo:")
        traceback.print_exc()
        return {"error": f"No se pudo obtener una respuesta del modelo de IA. Detalles: {str(e)}"}


def analizar_viabilidad_con_gemini(problema_usuario: str) -> dict:
    """
    Función que maneja la interacción completa con la API de Google Gemini.

    Similar a la función de Cerebras, pero adaptada a la estructura específica
    de la API de Gemini que tiene diferencias significativas en cómo se manejan
    las respuestas y configuraciones.

    Parámetros:
        problema_usuario: Descripción del problema a analizar

    Retorna:
        Diccionario con el análisis estructurado o diccionario de error
    """
    # Verificación de credenciales para Gemini (soporta dos nombres de variable)
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "API Key de Gemini no configurada en el servidor."}

    try:
        # Configuración inicial de la biblioteca de Google
        genai.configure(api_key=api_key)

        # Configuración especial para forzar salida JSON pura
        # Esto es crucial para obtener respuestas estructuradas consistentes
        generation_config = types.GenerationConfig(
            response_mime_type="application/json",
            # Nota: Gemini 2.5 Flash tiene capacidades nativas de razonamiento,
            # pero el prompt estructurado sigue siendo fundamental para consistencia
        )

        # Inicialización del modelo con configuración específica
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",  # Versión más reciente y capaz de Gemini
            generation_config=generation_config,
        )

        prompt_final = disenar_prompt_robusto(problema_usuario)

        # Validar que el prompt se generó correctamente
        if prompt_final is None:
            print("Error: disenar_prompt_robusto devolvió None")
            return {"error": "Error interno al generar el prompt de análisis."}

        if not isinstance(prompt_final, str) or prompt_final.strip() == "":
            print(f"Error: prompt_final no es string válido: {type(prompt_final)}")
            return {"error": "Error interno al generar el prompt de análisis."}

        print(f"Prompt para Gemini: '{prompt_final[:500]}...'")
        print(f"Longitud del prompt Gemini: {len(prompt_final)}")

        # Generación de respuesta usando el modelo configurado
        response = model.generate_content(prompt_final)

        # Validación exhaustiva de la respuesta de Gemini - su estructura es diferente a Cerebras
        print(f"Tipo de response Gemini: {type(response)}")
        print(f"Response Gemini es None: {response is None}")

        if not response:
            print("Respuesta de Gemini es None o falsy")
            print(f"Valor de response: {response}")
            return {"error": "La API de Gemini no devolvió una respuesta válida."}

        print(f"Atributos disponibles en response Gemini: {[attr for attr in dir(response) if not attr.startswith('_')]}")

        # Gemini tiene múltiples formas de acceder al texto, necesitamos verificar todas
        if hasattr(response, 'text'):
            print(f"Response tiene atributo text: {response.text is not None}")
        else:
            print("Response NO tiene atributo text")

        # Verificación de la estructura candidates (forma principal de Gemini)
        if hasattr(response, 'candidates'):
            print(f"Response tiene candidates: {len(response.candidates) if response.candidates else 0}")
            if response.candidates:
                print(f"Primer candidate tipo: {type(response.candidates[0])}")
                if hasattr(response.candidates[0], 'content'):
                    print(f"Primer candidate tiene content: {response.candidates[0].content}")
                    if hasattr(response.candidates[0].content, 'parts'):
                        print(f"Content tiene parts: {len(response.candidates[0].content.parts) if response.candidates[0].content.parts else 0}")
        else:
            print("Response NO tiene atributo candidates")

        # Extracción del texto de respuesta - Gemini tiene estructura más compleja que Cerebras
        raw_content = None

        # Primer método: acceso directo al atributo text (forma más simple)
        if hasattr(response, 'text') and response.text:
            raw_content = response.text
            print("Texto extraído del atributo 'text'")

        # Segundo método: navegación por la estructura candidates/parts (forma estándar de Gemini)
        elif hasattr(response, 'candidates') and response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content:
                if hasattr(candidate.content, 'parts') and candidate.content.parts and len(candidate.content.parts) > 0:
                    part = candidate.content.parts[0]
                    if hasattr(part, 'text') and part.text:
                        raw_content = part.text
                        print("Texto extraído de candidates[0].content.parts[0].text")

        if raw_content is None:
            print("No se pudo extraer texto de la respuesta de Gemini")
            print(f"Response completo: {response}")
            return {"error": "La respuesta de Gemini no contiene texto válido en ningún formato esperado."}

        print(f"Respuesta Gemini cruda: '{raw_content[:500]}...'")
        print(f"Tipo de respuesta Gemini: {type(raw_content)}")
        print(f"Longitud de respuesta Gemini: {len(raw_content) if raw_content else 0}")

        # Verificar si el texto está vacío
        if not isinstance(raw_content, str) or raw_content.strip() == "":
            print("La respuesta de Gemini está vacía o no es string")
            return {"error": "La respuesta del modelo de Gemini está vacía."}

        # Cargar la respuesta de texto en un diccionario de Python
        try:
            resultado_dict = json.loads(raw_content)
        except json.JSONDecodeError as e:
            print(f"Error al parsear JSON de Gemini: {e}")
            print(f"Contenido que falló: '{raw_content[:500]}...'")
            return {"error": f"La respuesta del modelo no es un JSON válido. Detalles: {str(e)}"}

        return resultado_dict

    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON de la API de Gemini: {e}")
        return {"error": f"La respuesta del modelo no es un JSON válido. Detalles: {str(e)}"}
    except Exception as e:
        print(f"Error al llamar a la API de Gemini o al procesar su respuesta: {e}")
        return {"error": f"No se pudo obtener una respuesta del modelo de IA. Detalles: {str(e)}"}


def analizar_viabilidad(model: str, problema_usuario: str) -> dict:
    """
    Función principal y unificada para análisis de viabilidad usando IA.

    Esta función actúa como punto de entrada único para el análisis,
    permitiendo al usuario elegir entre diferentes modelos de IA disponibles.
    Actualmente soporta Gemini y Cerebras, pero está diseñada para ser
    extensible a otros modelos en el futuro.

    Parámetros:
        model: Nombre del modelo a usar ('gemini' o 'cerebras')
        problema_usuario: Descripción del problema o proyecto a analizar

    Retorna:
        Diccionario con el análisis completo o mensaje de error
    """
    if model == 'gemini':
        return analizar_viabilidad_con_gemini(problema_usuario)
    elif model == 'cerebras':
        return analizar_viabilidad_con_cerebras(problema_usuario)
    else:
        return {"error": "Modelo no soportado. Usa 'gemini' o 'cerebras'."}