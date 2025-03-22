#!/bin/bash

# Variables
RESOURCE_GROUP="chatbots"
LOCATION="West US 2 "
REGISTRY_NAME="acragentess"
REGISTRY_LOGIN_SERVER="acragentess.azurecr.io"
IMAGE_VERSION=$(date +"%Y%m%d%H%M%S")
IMAGE_NAME="agentsapp:$IMAGE_VERSION"
CONTAINER_APP_NAME="gopapa-backend"

# Login en ACR
echo "Iniciando sesión en ACR..."
az acr login --name $REGISTRY_NAME
if [ $? -ne 0 ]; then
    echo "Error al iniciar sesión en ACR."
    exit 1
fi

# Asumiendo que YA estás en la carpeta backend/ al ejecutar el script
echo "Construyendo la imagen Docker..."
docker build \
  -t $REGISTRY_LOGIN_SERVER/$IMAGE_NAME \
  -f Dockerfile \
  .
if [ $? -ne 0 ]; then
    echo "Error al construir la imagen Docker."
    exit 1
fi

echo "Empujando la imagen Docker a ACR..."
docker push $REGISTRY_LOGIN_SERVER/$IMAGE_NAME
if [ $? -ne 0 ]; then
    echo "Error al empujar la imagen Docker a ACR."
    exit 1
fi
echo "Imagen Docker empujada a ACR."

echo "Actualizando Container App con la nueva imagen..."
az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $REGISTRY_LOGIN_SERVER/$IMAGE_NAME
if [ $? -ne 0 ]; then
    echo "Error al actualizar la aplicación en Container Apps."
    exit 1
fi

echo "Deploy completado correctamente."
