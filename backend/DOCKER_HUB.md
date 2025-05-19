# Publicar la imagen en Docker Hub

Este documento contiene instrucciones para publicar la imagen Docker de Image Classifier AI en Docker Hub.

## Requisitos previos

- Una cuenta en [Docker Hub](https://hub.docker.com/)
- Docker instalado en tu sistema
- Estar autenticado en Docker Hub desde tu terminal

## Pasos para publicar la imagen

### 1. Autenticarse en Docker Hub

```bash
docker login
```

Se te pedirá tu nombre de usuario y contraseña de Docker Hub.

### 2. Construir la imagen con una etiqueta

```bash
# Reemplaza 'yourusername' con tu nombre de usuario de Docker Hub
docker build -t yourusername/image-classifier-ai:latest .
```

### 3. Publicar la imagen

```bash
docker push yourusername/image-classifier-ai:latest
```

### 4. Verificar la publicación

Visita tu perfil de Docker Hub para verificar que la imagen se ha publicado correctamente.

## Uso de la imagen publicada

Una vez publicada la imagen, otros usuarios pueden utilizarla con el siguiente comando:

```bash
docker run -d -p 5000:5000 \
  -e OPENAI_API_KEY=your_api_key \
  -e MONGO_URI=your_mongo_uri \
  -e MONGO_DB_NAME=your_db_name \
  -e DB_STORAGE_TYPE=mongodb \
  yourusername/image-classifier-ai:latest
```

O utilizando el archivo `docker-compose.hub.yml` incluido:

```bash
# Edita docker-compose.hub.yml para cambiar 'yourusername' por tu nombre de usuario
docker-compose -f docker-compose.hub.yml up -d
```

## Etiquetas adicionales

Es una buena práctica etiquetar tus imágenes con versiones:

```bash
# Añadir una etiqueta de versión
docker build -t yourusername/image-classifier-ai:1.0.0 .
docker push yourusername/image-classifier-ai:1.0.0

# También actualizar la etiqueta 'latest'
docker push yourusername/image-classifier-ai:latest
```

## Mantener la imagen actualizada

Cuando realices cambios en la aplicación:

1. Actualiza el número de versión
2. Reconstruye la imagen
3. Publica la imagen con la nueva etiqueta
4. Actualiza también la etiqueta 'latest'
