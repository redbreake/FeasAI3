# FeasAI3 - Analizador de Viabilidad con IA

[![Django](https://img.shields.io/badge/Django-5.2.5-green.svg)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Una aplicación web Django avanzada que utiliza modelos de lenguaje de IA (Gemini y Cerebras) para analizar la viabilidad de proyectos empresariales, proporcionando evaluaciones detalladas y métricas personalizadas.

## 🚀 Características Principales

### 📊 Análisis Inteligente
- **Evaluación Multifactorial**: Análisis completo de viabilidad considerando factores técnicos, económicos, de mercado y riesgos.
- **Modelos de IA Avanzados**: Integración con Gemini (Google) y Cerebras para análisis sofisticados.
- **Puntuaciones Objetivas**: Sistema de calificación numérica para diferentes aspectos del proyecto.

### 👥 Gestión de Usuarios
- **Sistema de Autenticación**: Registro y login seguro de usuarios.
- **Perfiles Personalizados**: Gestión de usuarios con Django auth.
- **Historial Personal**: Seguimiento de todas las consultas realizadas.

### 📈 Dashboard Interactivo
- **Métricas en Tiempo Real**: Visualización de estadísticas de uso y rendimiento.
- **Análisis de Tendencias**: Gráficos y reportes sobre categorías de proyectos.
- **Panel Administrativo**: Interfaz completa para gestión del sistema.

### 🛡️ Arquitectura Robusta
- **Backend Django**: Framework web escalable y seguro.
- **Base de Datos SQLite**: Almacenamiento eficiente y portable.
- **API REST**: Arquitectura preparada para integraciones futuras.
- **Sistema de Testing**: Cobertura completa con pytest.

## 🏗️ Arquitectura del Sistema

```
FeasAI3/
├── analizador_viabilidad/    # Configuración principal de Django
├── core/                     # Lógica principal de negocio
│   ├── llm_service.py        # Integración con modelos de IA
│   ├── models.py            # Modelos de datos
│   ├── utils.py             # Utilidades y helpers
│   └── views.py             # Controladores web
├── usuarios/                 # Gestión de usuarios
├── dashboard/               # Panel de métricas
├── templates/               # Plantillas HTML
├── static/                  # Archivos estáticos
└── tests/                   # Suite de pruebas
```

## 📋 Requisitos del Sistema

- **Python**: 3.8 o superior
- **Django**: 4.2+
- **Base de Datos**: SQLite (incluida por defecto)
- **APIs Externas**:
  - Google Gemini API
  - Cerebras Cloud API (opcional)

## 🛠️ Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/redbreake/FeasAI3.git
cd FeasAI3
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` en el directorio `analizador_viabilidad/`:

```env
GOOGLE_API_KEY=tu_clave_api_de_google_gemini
CEREBRAS_API_KEY=tu_clave_api_de_cerebras  # Opcional
DEBUG=True
SECRET_KEY=tu_clave_secreta_django_segura
```

> **⚠️ Importante**: Nunca subas el archivo `.env` al repositorio. Está excluido en `.gitignore`.

### 5. Ejecutar Migraciones

```bash
python manage.py migrate
```

### 6. Crear Superusuario (Opcional)

```bash
python manage.py createsuperuser
```

### 7. Iniciar Servidor de Desarrollo

```bash
python manage.py runserver
```

Accede a la aplicación en: `http://localhost:8000`

## 📖 Uso de la Aplicación

### Análisis de Viabilidad

1. **Accede a la página principal** después de iniciar sesión.
2. **Describe tu proyecto** en el formulario principal.
3. **Selecciona el modelo de IA** (Gemini recomendado).
4. **Obtén el análisis** con métricas detalladas.

### Dashboard

- **Visualiza métricas** de uso del sistema.
- **Revisa estadísticas** de proyectos analizados.
- **Administra usuarios** (si eres administrador).

## 🔧 Configuración de APIs

### Google Gemini
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una nueva API Key
3. Agrega la key al archivo `.env`

### Cerebras (Opcional)
1. Regístrate en [Cerebras Cloud](https://cloud.cerebras.ai/)
2. Obtén tu API Key
3. Agrega la key al archivo `.env`

## 🧪 Testing

Ejecuta la suite completa de pruebas:

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=.

# Tests específicos
pytest core/tests/
pytest usuarios/tests/
pytest dashboard/tests/
```

## 🚀 Despliegue en Producción

### Variables de Entorno para Producción

```env
DEBUG=False
SECRET_KEY=tu_clave_secreta_muy_segura
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DATABASE_URL=postgresql://user:password@host:port/database
```

### Usando Docker (Recomendado)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "analizador_viabilidad.wsgi:application"]
```

## 🤝 Contribuir

1. **Fork** el proyecto
2. **Crea una rama** para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abre un Pull Request**

### Guías de Contribución

- Sigue los estándares de código PEP 8
- Agrega tests para nuevas funcionalidades
- Actualiza la documentación según corresponda
- Usa commits descriptivos

## 📝 API Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Página principal |
| `/analizar/` | POST | Análisis de viabilidad |
| `/historial/` | GET | Historial de consultas |
| `/dashboard/` | GET | Panel de métricas |
| `/admin/` | GET | Panel administrativo |

## 🐛 Reporte de Problemas

Si encuentras un bug o tienes una sugerencia:

1. Revisa los [Issues](https://github.com/redbreake/FeasAI3/issues) existentes
2. Crea un nuevo Issue con:
   - Descripción detallada del problema
   - Pasos para reproducirlo
   - Información del entorno (Python, Django, etc.)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- **Google** por la API de Gemini
- **Cerebras** por sus modelos de IA
- **Django Project** por el excelente framework
- Comunidad open source

---

**Desarrollado con ❤️ por [redbreake](https://github.com/redbreake)**