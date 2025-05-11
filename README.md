# Clasificador de Imágenes con IA

## Descripción General
Este proyecto es una aplicación de Clasificador de Imágenes que permite a los usuarios subir imágenes y recibir una clasificación automática en categorías predefinidas. La aplicación utiliza la API de OpenAI para la clasificación de imágenes y proporciona una API REST para interacción.

## Características
- Subida de imágenes a través de endpoints de API.
- Clasificación automática de imágenes en categorías predefinidas (perro, gato, auto, árbol, etc.).
- Devolución de resultados de clasificación, incluyendo categoría predicha y nivel de confianza.
- Caché de resultados para mejorar el rendimiento en imágenes procesadas previamente.
- Estadísticas de uso y rendimiento del clasificador.
- Manejo de errores y retroalimentación durante el procesamiento de imágenes.

## Tecnologías Utilizadas
- **Backend**: Python (Flask)
- **Clasificación de Imágenes**: API de OpenAI (modelo gpt-4o con capacidades de visión)
- **Documentación**: Swagger UI

## Estructura del Proyecto
```
clasificador-de-imagenes
└── backend
    ├── app.py               # Punto de entrada para la aplicación
    ├── config.py            # Configuración general
    ├── requirements.txt     # Paquetes requeridos
    ├── test_api.py          # Script de prueba
    ├── TESTING.md           # Documentación de pruebas
    ├── api/                 # Endpoints de API
    │   ├── __init__.py
    │   └── routes.py        # Definiciones de rutas de API
    ├── models/              # Modelos para clasificación
    │   └── image_classifier.py  # Clasificador con OpenAI
    ├── static/              # Archivos estáticos
    │   └── swagger.json     # Documentación de API en Swagger
    └── utils/               # Funciones de utilidad
        ├── __init__.py
        └── image_processing.py  # Utilidades de procesamiento de imágenes
```

## Instrucciones de Configuración

### Backend
1. Navegar al directorio `backend`.
2. Instalar las dependencias requeridas:
   ```
   pip install -r requirements.txt
   ```
3. Configurar la clave API de OpenAI en un archivo `.env` (ver `.env.example`).
4. Ejecutar el servidor backend:
   ```
   python app.py
   ```

### Tests
Para ejecutar los tests unitarios:
```
cd backend
python -m unittest discover tests
```

## Uso de la API
- Documentación de API disponible en `/api/docs` cuando el servidor está ejecutándose
- Probar la API usando el script `test_api.py` incluido
- Endpoints de ejemplo:
  - GET `/api/categories`: Obtener todas las categorías disponibles
  - POST `/api/classify`: Clasificar una imagen subida
  - GET `/api/stats`: Obtener estadísticas de clasificación
  - GET `/api/test-openai`: Probar la conexión con la API de OpenAI

## Contribuciones
¡Las contribuciones son bienvenidas! Por favor, siéntete libre de enviar un pull request o abrir un issue para cualquier sugerencia o mejora.

## Licencia
Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.
