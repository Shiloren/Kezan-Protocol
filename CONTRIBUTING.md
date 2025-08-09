# Guía de Contribución

¡Gracias por tu interés en contribuir al Kezan Protocol! Esta guía te ayudará a configurar tu entorno de desarrollo y a entender nuestro proceso de contribución.

## Configuración del Entorno

### Requisitos Previos
- Python 3.12+
- Node.js 18+
- Rust (para Tauri)

### Pasos de Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/Shiloren/Kezan-Protocol.git
cd Kezan-Protocol
```

2. Configura el entorno Python:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Configura el frontend:
```bash
cd frontend
npm install
```

## Estructura del Proyecto

- `/kezan/` - Código fuente principal de Python
- `/frontend/` - Aplicación Tauri/React
- `/tests/` - Tests unitarios y de integración
- `/docs/` - Documentación

## Guías de Estilo

### Python
- Seguimos PEP 8
- Usamos type hints
- Documentamos funciones y clases con docstrings

### JavaScript/React
- Usamos ESLint y Prettier
- Componentes funcionales con hooks
- Props tipadas con PropTypes

## Proceso de Contribución

1. Crea un fork del repositorio
2. Crea una rama para tu feature: `git checkout -b feature/nombre-feature`
3. Desarrolla tu feature siguiendo las guías de estilo
4. Asegúrate de que los tests pasan: `pytest tests/`
5. Crea un Pull Request con una descripción clara de los cambios

## Tests

- Ejecuta tests Python: `pytest tests/`
- Ejecuta tests Frontend: `cd frontend && npm test`

## Reportar Bugs

Usa los issues de GitHub para reportar bugs. Incluye:
- Descripción clara del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Screenshots si aplica
- Información del entorno

## Contacto

Para preguntas o dudas, puedes:
- Abrir un issue
- Contactar al equipo mediante [medio de contacto preferido]

¡Gracias por contribuir!
