# Etapa de construcción del frontend
FROM node:16 AS build

WORKDIR /app

# Deshabilita la verificación estricta de SSL (opcional)
RUN npm config set strict-ssl false

# Copia solo los archivos necesarios para instalar dependencias
COPY package.json package-lock.json ./

# Instala las dependencias sin usar caché innecesario
RUN npm ci

# Copia el resto de los archivos del proyecto
COPY . ./

# Construye la aplicación y genera la versión estática
RUN npm run build && npm run export

# Etapa final: Servir con Nginx
FROM nginx:stable-alpine AS production

# Directorio de trabajo para Nginx
WORKDIR /usr/share/nginx/html

# Copia la aplicación exportada (la carpeta por defecto es "out")
COPY --from=build /app/out ./

# Expone el puerto 80
EXPOSE 80

# Comando de inicio
CMD ["nginx", "-g", "daemon off;"]