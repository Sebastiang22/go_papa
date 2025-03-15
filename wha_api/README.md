# 🤖 Cliente de WhatsApp con Python

Este proyecto proporciona una interfaz en Python para interactuar con WhatsApp Web, permitiendo enviar mensajes y monitorear conversaciones en tiempo real.

## 📋 Requisitos Previos

1. **Python 3.7 o superior**
2. **Node.js 14 o superior**
3. **WhatsApp Web** (sesión activa)

## 🚀 Instalación

### 1. Servidor WhatsApp (Node.js)

```bash
# Instalar dependencias del servidor
cd whatsapp-bot
npm install

# Iniciar el servidor
node index.js
```

### 2. Cliente Python

```bash
# Crear y activar entorno virtual (recomendado)
python -m venv venv_whatsapp
source venv_whatsapp/bin/activate  # En Windows: venv_whatsapp\Scripts\activate

# Instalar dependencias de Python
pip install python-socketio websockets
```

## 💻 Uso del Cliente

Hay dos scripts principales disponibles:

### 1. Monitor de Mensajes (`monitor_mensajes.py`)

Muestra en tiempo real los mensajes entrantes de WhatsApp.

```bash
python monitor_mensajes.py
```

**Características:**
- 📱 Muestra mensajes entrantes en tiempo real
- 🕒 Incluye marca de tiempo
- 👤 Muestra nombre del remitente y número
- 📝 Soporta mensajes de texto y multimedia
- ⚡ Reconexión automática

Para salir: Presiona `Ctrl+C`

### 2. Cliente Interactivo (`enviar_mensaje.py`)

Permite enviar mensajes de WhatsApp desde la terminal.

```bash
python enviar_mensaje.py
```

**Características:**
- ✉️ Envío de mensajes a cualquier número
- 📝 Soporte para mensajes multilínea
- 🔄 Reconexión automática
- 📊 Muestra estado de conexión
- ✨ Interfaz interactiva

**Menú de Opciones:**
1. Enviar mensaje
2. Reconectar
3. Salir

**Formato de Números:**
- Usar formato internacional sin '+' ni espacios
- Ejemplo: `573143604303`

## 📱 Ejemplos de Uso

### Enviar un Mensaje

1. Ejecutar el cliente interactivo:
```bash
python enviar_mensaje.py
```

2. Seleccionar opción 1 (Enviar mensaje)

3. Ingresar número:
```
Número (ej: 573143604303): 573143604303
```

4. Escribir mensaje (Enter dos veces para enviar):
```
Escriba el mensaje (presione Enter dos veces para enviar):
Hola, ¿cómo estás?

```

### Monitorear Mensajes

1. Ejecutar el monitor:
```bash
python monitor_mensajes.py
```

2. Los mensajes entrantes se mostrarán así:
```
==================================================
📱 [10:30:15] Mensaje de Juan Pérez
📞 Número: 573143604303
💬 Mensaje: Hola, ¿cómo estás?
==================================================
```

## ⚠️ Consideraciones Importantes

1. **Conexión WhatsApp Web**
   - Al iniciar por primera vez, escanear el código QR con WhatsApp
   - La sesión se mantiene activa hasta que se cierre manualmente

2. **Formato de Números**
   - Usar siempre formato internacional
   - Sin espacios, '+' o caracteres especiales
   - Mínimo 10 dígitos

3. **Estado de Conexión**
   - El cliente muestra el estado actual de conexión
   - Opción de reconexión manual disponible
   - Reconexión automática en caso de desconexión

4. **Mensajes Multimedia**
   - El monitor puede detectar mensajes multimedia
   - Se mostrará "Mensaje multimedia" para fotos/videos

## 🔧 Solución de Problemas

1. **Error de Conexión**
   - Verificar que el servidor Node.js esté corriendo
   - Usar opción "Reconectar" en el menú
   - Revisar conexión a Internet

2. **Mensaje No Enviado**
   - Verificar formato del número
   - Comprobar estado de conexión
   - Intentar reconectar y enviar nuevamente

3. **Sesión Cerrada**
   - Reiniciar servidor Node.js
   - Escanear código QR nuevamente
   - Verificar WhatsApp Web

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles. 