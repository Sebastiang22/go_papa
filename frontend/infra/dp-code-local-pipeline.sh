#!/bin/bash

# Variables (ajusta según tu entorno)
RESOURCE_GROUP="chatbots"
LOCATION="West US 2"
STATIC_WEB_APP_NAME="wa-gopapa"
# Si estás en la carpeta frontend y usas Vue, el output por defecto es "dist"
FRONTEND_ARTIFACT_LOCATION="dist"

echo "Iniciando el deploy de la Static Web App..."

# Opcional: Construir el frontend
# npm install && npm run build

# Desplegar la Static Web App usando la CLI de Azure
az staticwebapp upload \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --output-location $FRONTEND_ARTIFACT_LOCATION

if [ $? -ne 0 ]; then
    echo "Error en el despliegue de la Static Web App."
    exit 1
fi

echo "Deploy completado correctamente."
