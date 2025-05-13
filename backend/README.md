# Clasificador de Imágenes con OpenAI - Backend

## Descripción general
Este backend sirve como el núcleo del proyecto de Clasificador de Imágenes con IA. Es responsable de gestionar la subida de imágenes, procesarlas y devolver los resultados de clasificación basados en un conjunto predefinido de categorías. El backend está construido con Flask e integra la API de OpenAI Vision para la clasificación de imágenes.

## Características
- Subida de imágenes para clasificación automática
- Clasificación en categorías predefinidas (perro, gato, auto, árbol, etc.)
- Respuesta con la categoría predicha y nivel de confianza
- Validación de tipos de archivos (solo JPEG y PNG)
- Límite de tamaño de archivo (5MB máximo)

## Tecnologías utilizadas
- Python
- Flask
- OpenAI Vision API (modelo GPT-4 Vision)
- Pillow (Biblioteca de procesamiento de imágenes)
- python-dotenv (para variables de entorno)
- MongoDB (para almacenamiento de datos)
- ImageBB API (para almacenamiento de imágenes)

## Instrucciones de configuración

### Prerrequisitos
- Python 3.7 o superior
- pip (instalador de paquetes de Python)
- MongoDB (opcional, para almacenamiento de datos)

### Instalación
1. Clonar el repositorio:
   ```
   git clone <url-del-repositorio>
   cd image-classifier-ai/backend
   ```

2. Instalar los paquetes requeridos:
   ```
   pip install -r requirements.txt
   ```

3. Configurar las variables de entorno:
   - Copiar el archivo `.env.example` a `.env` (o crear uno nuevo)
   - Establecer la clave API de OpenAI en el archivo `.env`:
     ```
     OPENAI_API_KEY=tu_clave_api_aquí
     ```

### Ejecución de la aplicación
1. Iniciar el servidor:
   ```
   python app.py
   ```

2. La API estará disponible en `http://localhost:5000` (o el puerto especificado).

## Endpoints de la API

### GET /
- **Descripción**: Página principal de la API
- **Respuesta**: Información básica sobre la API y sus endpoints disponibles

### GET /api/categories
- **Descripción**: Obtiene todas las categorías disponibles para clasificación
- **Respuesta**: Lista de categorías en formato JSON
  ```json
  {
    "categories": ["perro", "gato", "auto", "árbol", ...]
  }
  ```

### POST /api/classify
- **Descripción**: Clasifica una imagen subida
- **Petición**: Formulario multipart con un campo 'file' que contiene la imagen
- **Respuesta**: Resultado de la clasificación en formato JSON
  ```json
  {
    "category": "perro",
    "confidence": 95.5,
    "categories": ["perro", "gato", "auto", "árbol", ...]
  }
  ```
- **Códigos de error**:
  - 400: Error de validación (tipo de imagen incorrecto, tamaño excesivo, etc.)
  - 413: Archivo demasiado grande
  - 500: Error interno del servidor

## Estructura de directorios
- `app.py`: Punto de entrada para la aplicación backend.
- `models/image_classifier.py`: Contiene la lógica de clasificación utilizando OpenAI.
- `api/routes.py`: Define los endpoints de la API.
- `utils/image_processing.py`: Funciones de utilidad para el procesamiento de imágenes.
- `utils/mongodb_stats.py`: Gestor de estadísticas basado en MongoDB.
- `utils/stats_new.py`: Gestor de estadísticas basado en archivos.
- `utils/imagebb.py`: Integración con ImageBB para almacenamiento de imágenes.
- `utils/db.py`: Utilidades para conexión a MongoDB.
- `utils/setup_mongodb.py`: Script para configurar MongoDB.
- `utils/migrate_to_mongodb.py`: Script para migrar datos a MongoDB.
- `config.py`: Configuración de la aplicación.

## Configuración de la base de datos

La aplicación soporta dos modos de almacenamiento de datos:

### 1. Almacenamiento basado en archivos (predeterminado)
- Las estadísticas se almacenan en `stats/classification_stats.json`
- Los metadatos de las imágenes se almacenan en `stats/history/*.json`
- Las imágenes se suben a ImageBB

### 2. Almacenamiento en MongoDB
- Las estadísticas y metadatos se almacenan en colecciones de MongoDB
- Las imágenes se siguen subiendo a ImageBB

Para configurar MongoDB:

1. Ejecutar el script de configuración:
   ```
   python utils/setup_mongodb.py
   ```
   El script te guiará a través del proceso de configuración.

2. Alternativamentee, puedes configurar manualmente las siguientes variables en el archivo `.env`:
   ```
   DB_STORAGE_TYPE=mongodb
   MONGO_URI=mongodb://localhost:27017  # O tu URI de MongoDB Atlas
   MONGO_DB_NAME=image_classifier_db
   ```

3. Para migrar datos existentes de archivos a MongoDB:
   ```
   python utils/migrate_to_mongodb.py
   ```

### Estructura de la base de datos MongoDB
- **Colección `classifications`**: Almacena registros individuales de clasificación con metadatos de imágenes
- **Colección `statistics`**: Almacena estadísticas globales agregadas
- **Colección `daily_stats`**: Almacena estadísticas diarias de clasificación

## Categorías predefinidas
- perro
- gato
- auto
- árbol
- ave
- persona
- edificio
- flor
- paisaje
- alimento

## Contribuciones
¡Las contribuciones son bienvenidas! Por favor, envía un pull request o abre un issue para cualquier mejora o corrección de errores.

## Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.