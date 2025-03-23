# Etapa 1: Construcción
FROM node:18-alpine AS builder

# Creamos y usamos el directorio de trabajo
WORKDIR /app

# Copiamos los archivos que definen las dependencias
COPY package.json package-lock.json ./

# Instalamos dependencias
RUN npm install

# Copiamos el resto del código
COPY . .

# Construimos la aplicación de Next.js
RUN npm run build


# Etapa 2: Imagen final para producción
FROM node:18-alpine AS runner

# Directorio de trabajo
WORKDIR /app

# Copiamos los archivos esenciales desde la imagen builder
COPY --from=builder /app/package.json /app/package-lock.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.mjs ./

# Instalamos solo las dependencias de producción
RUN npm install --production

# Definimos la variable de entorno para producción
ENV NODE_ENV=production
ENV PATH /app/node_modules/.bin:$PATH

# Exponemos el puerto por defecto de Next.js
EXPOSE 3000

# Comando de inicio
CMD ["/usr/local/bin/node", "/app/node_modules/.bin/next", "start"]
#