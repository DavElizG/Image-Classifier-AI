@echo off
:: Script para construir y ejecutar la aplicación en Docker en Windows

echo === Iniciando el despliegue de Image Classifier AI en Docker ===

:: Verificar si Docker está instalado
where docker >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Docker no está instalado. Por favor, instala Docker primero.
    exit /b 1
)

:: Verificar si Docker Compose está instalado
where docker-compose >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Docker Compose no está instalado. Por favor, instala Docker Compose primero.
    exit /b 1
)

:: Verificar si la variable de entorno OPENAI_API_KEY está configurada
IF "%OPENAI_API_KEY%"=="" (
    echo Advertencia: OPENAI_API_KEY no está configurada.
    echo Por favor, ingresa tu API key de OpenAI:
    set /p OPENAI_API_KEY="> "
) ELSE (
    echo API key de OpenAI detectada en variables de entorno.
)

:: Verificar si la variable de entorno MONGO_URI está configurada
IF "%MONGO_URI%"=="" (
    echo Advertencia: MONGO_URI no está configurada.
    echo Por favor, ingresa tu URI de conexión a MongoDB:
    set /p MONGO_URI="> "
) ELSE (
    echo URI de MongoDB detectada en variables de entorno.
)

echo Construyendo imagen de Docker...
docker-compose build

echo Iniciando servicios...
docker-compose up -d

echo ==============================================
echo Image Classifier AI está ejecutándose en:
echo http://localhost:5001
echo ==============================================

echo Para ver los logs: docker-compose logs -f
echo Para detener: docker-compose down

pause
