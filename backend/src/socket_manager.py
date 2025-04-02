import socketio
import logging
import json
from typing import Dict, Any, List, Optional

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear servidor Socket.IO con parámetros mejorados
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # Para desarrollo. En producción, especificar orígenes
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=5 * 1024 * 1024,  # 5MB
    always_connect=True,  # Permitir siempre conexiones, incluso si hay errores iniciales
    logger=True,  # Habilitar logs del servidor
    engineio_logger=True  # Habilitar logs del engine
)

# Crear aplicación ASGI
app = socketio.ASGIApp(
    sio, 
    socketio_path='/api/socket.io',
    static_files={
        '/test': './static/socket_test.html',  # Página de prueba
    }
)

# Almacenar conexiones activas
active_connections = {}

@sio.event
async def connect(sid, environ):
    """
    Manejar eventos de conexión de clientes
    """
    logger.info(f"Cliente conectado: {sid}")
    active_connections[sid] = {'id': sid, 'connected_at': environ.get('SERVER_TIME', '')}
    
    # Emitir evento de actualización de estado de conexión
    await sio.emit('connection_status', {'status': 'connected', 'sid': sid, 'clients': len(active_connections)})
    
    # Log para debug
    logger.info(f"Conexiones activas: {len(active_connections)}")

@sio.event
async def disconnect(sid):
    """
    Manejar eventos de desconexión de clientes
    """
    logger.info(f"Cliente desconectado: {sid}")
    if sid in active_connections:
        del active_connections[sid]
    
    # Emitir evento de actualización de estado de conexión
    await sio.emit('connection_status', {'status': 'disconnected', 'clients': len(active_connections)})
    
    # Log para debug
    logger.info(f"Conexiones activas después de desconexión: {len(active_connections)}")

@sio.event
async def connect_error(sid, data):
    """
    Manejar errores de conexión
    """
    logger.error(f"Error de conexión para {sid}: {data}")
    await sio.emit('connection_error', {'error': str(data)})

async def get_server_status() -> Dict[str, Any]:
    """
    Obtener el estado actual del servidor WebSocket
    """
    return {
        "active_connections": len(active_connections),
        "connection_ids": list(active_connections.keys())
    }

async def emit_orders_update():
    """
    Emitir evento de actualización de órdenes a todos los clientes conectados
    """
    try:
        logger.info(f"Emitiendo actualización de órdenes a {len(active_connections)} clientes")
        await sio.emit('orders_update', {'timestamp': 'now'})
    except Exception as e:
        logger.error(f"Error al emitir actualización de órdenes: {str(e)}")

async def emit_order_deleted(order_id: str):
    """
    Emitir evento de orden eliminada a todos los clientes conectados
    """
    try:
        logger.info(f"Emitiendo evento de orden eliminada: {order_id}")
        await sio.emit('order_deleted', {'id': order_id})
    except Exception as e:
        logger.error(f"Error al emitir orden eliminada: {str(e)}")

async def emit_order_updated(order_id: str, new_state: str):
    """
    Emitir evento de orden actualizada a todos los clientes conectados
    """
    try:
        logger.info(f"Emitiendo evento de orden actualizada: {order_id} -> {new_state}")
        await sio.emit('order_updated', {'id': order_id, 'state': new_state})
    except Exception as e:
        logger.error(f"Error al emitir orden actualizada: {str(e)}")

async def emit_order_created(order_id: str):
    """
    Emitir evento de nueva orden a todos los clientes conectados
    """
    try:
        logger.info(f"Emitiendo evento de nueva orden: {order_id}")
        await sio.emit('order_created', {'id': order_id})
    except Exception as e:
        logger.error(f"Error al emitir nueva orden: {str(e)}") 