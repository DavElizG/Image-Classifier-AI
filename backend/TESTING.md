# Guía de Prueba de la API del Clasificador de Imágenes

Esta guía te ayudará a probar la API del Clasificador de Imágenes utilizando diferentes herramientas.

## Requisitos Previos

- Python 3.7 o superior
- Pip (gestor de paquetes de Python)
- Las dependencias instaladas (`pip install -r requirements.txt`)
- Conexión a internet para acceder a la API de OpenAI

## Iniciar el Servidor

Para iniciar el servidor, navega al directorio del backend y ejecuta:

```bash
python app.py
```

El servidor estará disponible en `http://localhost:5000`.

## Herramientas de Prueba

### 1. Script de Prueba Automatizado

Hemos incluido un script (`test_api.py`) que te permite probar rápidamente las funcionalidades principales de la API:

```bash
# Verificar que la API y OpenAI estén funcionando
python test_api.py

# Clasificar una imagen
python test_api.py --image ruta/a/tu/imagen.jpg

# Obtener estadísticas de uso
python test_api.py --stats
```

### 2. Documentación Swagger (OpenAPI)

La API incluye documentación interactiva con Swagger UI, disponible en:

```
http://localhost:5000/api/docs
```

Desde aquí puedes:
- Ver todos los endpoints disponibles
- Probar directamente los endpoints
- Ver ejemplos de respuestas

### 3. Usando cURL

#### Obtener Categorías
```bash
curl -X GET http://localhost:5000/api/categories
```

#### Probar Conexión con OpenAI
```bash
curl -X GET http://localhost:5000/api/test-openai
```

#### Clasificar una Imagen
```bash
curl -X POST -F "file=@ruta/a/tu/imagen.jpg" http://localhost:5000/api/classify
```

#### Obtener Estadísticas

```bash
curl -X GET "http://localhost:5000/api/stats?days=7" -H "accept: application/json"
```

Respuesta:
```json
{
  "stats": {
    "total_classifications": 42,
    "categories": {
      "perro": {
        "count": 15,
        "avg_confidence": 92.5
      },
      "gato": {
        "count": 10,
        "avg_confidence": 89.3
      },
      "..."
    },
    "daily": {
      "2025-05-10": {
        "total": 8,
        "categories": {
          "perro": 3,
          "gato": 2,
          "..."
        }
      },
      "..."
    },
    "last_updated": "2025-05-10T15:30:45.123456"
  }
}
```

### 4. Usando Python y Requests

```python
import requests

# Obtener categorías
response = requests.get("http://localhost:5000/api/categories")
print(response.json())

# Clasificar imagen
with open("ruta/a/tu/imagen.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:5000/api/classify", files=files)
    print(response.json())
```

## Ejemplos de Respuestas

### Categorías
```json
{
  "categories": [
    "perro", "gato", "auto", "árbol", "ave", 
    "persona", "edificio", "flor", "paisaje", "alimento"
  ]
}
```

### Clasificación de Imagen
```json
{
  "category": "perro",
  "confidence": 95.7,
  "categories": [
    "perro", "gato", "auto", "árbol", "ave", 
    "persona", "edificio", "flor", "paisaje", "alimento"
  ]
}
```

## Solución de Problemas

### Error: "OpenAI API connection failed"
Verifica que:
1. La clave API de OpenAI sea válida
2. La clave tenga permisos para acceder a los modelos de visión
3. La conexión a internet esté funcionando correctamente

### Error: "Invalid image type" o "File size exceeds the maximum limit"
Asegúrate de que:
1. La imagen sea JPG o PNG
2. El tamaño del archivo sea menor a 5MB

### Error: "No file part in the request"
Verifica que:
1. Estás enviando la imagen con el campo "file" en un formulario multipart/form-data
