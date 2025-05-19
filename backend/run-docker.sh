#!/bin/bash
# Script para construir y ejecutar la aplicación en Docker

# Definir colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Iniciando el despliegue de Image Classifier AI en Docker ===${NC}"

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null
then
    echo -e "${RED}Error: Docker no está instalado. Por favor, instala Docker primero.${NC}"
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null
then
    echo -e "${RED}Error: Docker Compose no está instalado. Por favor, instala Docker Compose primero.${NC}"
    exit 1
fi

# Verificar si la variable de entorno OPENAI_API_KEY está configurada
if [ -z "$OPENAI_API_KEY" ]
then
    echo -e "${YELLOW}Advertencia: OPENAI_API_KEY no está configurada.${NC}"
    echo -e "${YELLOW}Por favor, ingresa tu API key de OpenAI:${NC}"
    read -s apikey
    export OPENAI_API_KEY=$apikey
else
    echo -e "${GREEN}API key de OpenAI detectada en variables de entorno.${NC}"
fi

echo -e "${GREEN}Construyendo imagen de Docker...${NC}"
docker-compose build

echo -e "${GREEN}Iniciando servicios...${NC}"
docker-compose up -d

echo -e "${GREEN}==============================================${NC}"
echo -e "${GREEN}Image Classifier AI está ejecutándose en:${NC}"
echo -e "${GREEN}http://localhost:5000${NC}"
echo -e "${GREEN}==============================================${NC}"

echo -e "${YELLOW}Para ver los logs: ${NC}docker-compose logs -f"
echo -e "${YELLOW}Para detener: ${NC}docker-compose down"
