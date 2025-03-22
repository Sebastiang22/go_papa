
# Imagen base de Python
FROM python:3.9-slim

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copiamos primero requirements.txt para aprovechar la capa de cache
COPY backend/src/requirements.txt /app/

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de la aplicación
COPY backend/src/ /app/

# Creamos un usuario sin privilegios y asignamos permisos
RUN adduser --disabled-password --gecos '' myuser \
    && chown -R myuser:myuser /app

# Ajustamos las variables de entorno
ENV PORT=8000
EXPOSE 8000

# Cambiamos al usuario sin privilegios
USER myuser

# Indicamos cómo arrancar la aplicación
# Si "main_dev.py" es el script que lanza tu aplicación de FastAPI,
# y este script arranca un servidor (por ejemplo Uvicorn) internamente,
# puedes simplemente hacer:
# CMD ["python", "main_dev.py"]

# Si en cambio necesitas llamar uvicorn explícitamente:
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
