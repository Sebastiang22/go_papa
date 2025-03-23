#!/bin/bash

# Variables
RESOURCE_GROUP="chatbots"
LOCATION="West US 2"
REGISTRY_NAME="acragentess"
REGISTRY_LOGIN_SERVER="acragentess.azurecr.io"
IMAGE_VERSION=$(date +"%Y%m%d%H%M%S")
IMAGE_NAME="agentsfrontend:$IMAGE_VERSION"
WEB_APP_NAME="aw-gopapa"

# Deploy
echo "Iniciando el deploy..."

# Login en ACR
echo "Iniciando sesión en ACR..."
az acr login --name $REGISTRY_NAME
if [ $? -ne 0 ]; then
    echo "Error al iniciar sesión en ACR."
    exit 1
fi

# Build y push de la imagen Docker
echo "Construyendo la imagen Docker..."
docker build -t $REGISTRY_LOGIN_SERVER/$IMAGE_NAME .
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

# Despliegue de la aplicación
echo "Desplegando la aplicación..."
az deployment group create --resource-group $RESOURCE_GROUP --template-file infra/deploy/dp-WebApp-Container.bicep --parameters webAppName=$WEB_APP_NAME containerRegistryName=$REGISTRY_NAME imageName=$IMAGE_NAME
if [ $? -ne 0 ]; then
    echo "Error en el despliegue de la aplicación."
    exit 1
fi
echo "Despliegue completado."

echo "..."
echo "Deploy completado correctamente"