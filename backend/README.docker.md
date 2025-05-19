# Docker para Image Classifier AI

Este documento explica cómo usar Docker para ejecutar la aplicación Image Classifier AI.

## Requisitos previos

- Docker instalado en tu sistema ([Instalar Docker](https://docs.docker.com/get-docker/))
- Docker Compose instalado en tu sistema ([Instalar Docker Compose](https://docs.docker.com/compose/install/))
- Clave API de OpenAI válida

## Configuración rápida

1. Configura tu clave API de OpenAI:

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="tu-clave-api-openai"

# Linux/macOS
export OPENAI_API_KEY="tu-clave-api-openai"
```

2. Inicia la aplicación:

```bash
docker-compose up -d
```

3. Accede a la aplicación en: [http://localhost:5000](http://localhost:5000)

## Configuración detallada

### Variables de entorno

Puedes modificar el archivo `docker-compose.yml` para cambiar estas configuraciones:

- `DEBUG`: Modo de depuración (True/False)
- `HOST`: Host donde se ejecuta la aplicación (0.0.0.0 para permitir conexiones externas)
- `PORT`: Puerto donde se expone la aplicación
- `MONGO_URI`: URI de conexión a MongoDB
- `MONGO_DB_NAME`: Nombre de la base de datos MongoDB
- `DB_STORAGE_TYPE`: Tipo de almacenamiento (mongodb)
- `OPENAI_API_KEY`: Clave API de OpenAI (sensible, se recomienda pasar como variable de entorno)

### Volúmenes

El Docker Compose monta estos volúmenes:

- `./cache:/app/cache`: Caché de clasificaciones para evitar solicitudes repetidas a OpenAI
- `./stats:/app/stats`: Estadísticas y historial de clasificaciones

## Manejo de la aplicación con Docker

### Ver logs

```bash
docker-compose logs -f
```

### Detener la aplicación

```bash
docker-compose down
```

### Reiniciar la aplicación

```bash
docker-compose restart
```

### Reconstruir la imagen

```bash
docker-compose build --no-cache
docker-compose up -d
```

## Solución de problemas

### Error de conexión a MongoDB

Asegúrate de que la URI de MongoDB sea accesible desde dentro del contenedor Docker.

### Error de clave API de OpenAI

Verifica que la variable de entorno `OPENAI_API_KEY` esté correctamente configurada.

### Errores de permisos en los volúmenes

Puede que necesites ajustar los permisos:

```bash
# En sistemas basados en Linux
chmod -R 777 cache stats
```
