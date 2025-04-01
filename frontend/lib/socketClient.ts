import { io, Socket } from 'socket.io-client';
import type { EventHandlerMap } from 'socket.io/dist/typed-events';

export interface OrderUpdateCallback {
  (): void;
}

export interface OrderDeletedCallback {
  (orderId: string): void;
}

export interface OrderUpdatedCallback {
  (orderId: string, state: string): void;
}

export interface OrderCreatedCallback {
  (orderId: string): void;
}

export interface ConnectionStatusCallback {
  (status: { status: string; sid?: string; clients: number }): void;
}

let socket: Socket | null = null;
let isDummySocket = false;
const SOCKET_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// Opciones mejoradas de conexión
const socketOptions = {
  autoConnect: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 3000,
  timeout: 10000,
  transports: ['websocket', 'polling'],
  path: '/api/socket.io/'
};

// Crear un socket dummy para el caso de que la conexión falle
function createDummySocket(): Socket {
  console.warn('⚠️ Usando socket dummy debido a fallos de conexión al servidor');
  const dummySocket: any = {
    connected: false,
    id: 'dummy-socket',
    on: (event: string, callback: any) => {
      console.log(`📢 Dummy socket: evento '${event}' registrado`);
      return () => {}; // Devuelve una función de cancelación de suscripción simulada
    },
    off: (event: string) => {
      console.log(`📢 Dummy socket: evento '${event}' eliminado`);
    },
    disconnect: () => {
      console.log('📢 Dummy socket: desconexión simulada');
    },
    connect: () => {
      console.log('📢 Dummy socket: conexión simulada');
    }
  };
  
  return dummySocket as Socket;
}

// Obtener el socket (inicializándolo si es necesario)
export function getSocket(): Socket {
  if (!socket) {
    console.log('🔄 Inicializando Socket.IO con opciones:', socketOptions);
    initializeSocket();
  }
  return socket!;
}

// Inicializar la conexión Socket.IO
export function initializeSocket(): void {
  if (socket) {
    console.log('🔄 Socket ya inicializado, reconectando...');
    socket.connect();
    return;
  }

  try {
    console.log(`🔄 Conectando a: ${SOCKET_URL}`);
    socket = io(SOCKET_URL, socketOptions);
    isDummySocket = false;

    // Eventos de conexión generales
    socket.on('connect', () => {
      console.log(`✅ Socket.IO conectado: ${socket?.id}`);
    });

    socket.on('disconnect', (reason) => {
      console.log(`❌ Socket.IO desconectado: ${reason}`);
    });

    socket.on('reconnect', (attempt) => {
      console.log(`🔄 Socket.IO reconectado después de ${attempt} intentos`);
    });

    socket.on('reconnect_attempt', (attempt) => {
      console.log(`🔄 Socket.IO intento de reconexión #${attempt}`);
    });

    socket.on('reconnect_error', (error) => {
      console.error(`❌ Error de reconexión Socket.IO:`, error);
    });

    socket.on('reconnect_failed', () => {
      console.error(`❌ Reconexión Socket.IO fallida después de ${socketOptions.reconnectionAttempts} intentos`);
      // Si no podemos reconectar, usamos un socket dummy para evitar errores
      socket = createDummySocket();
      isDummySocket = true;
    });

    socket.on('error', (error) => {
      console.error(`❌ Error Socket.IO:`, error);
    });

    socket.on('connect_error', (error) => {
      console.error(`❌ Error de conexión Socket.IO:`, error);
      if (!isDummySocket && socket?.connected === false) {
        console.error('⚠️ No se pudo conectar al servidor WebSocket, usando socket dummy');
        socket = createDummySocket();
        isDummySocket = true;
      }
    });

  } catch (error) {
    console.error('❌ Error al inicializar Socket.IO:', error);
    // En caso de error, usar un socket dummy para evitar errores
    socket = createDummySocket();
    isDummySocket = true;
  }
}

// Cerrar la conexión
export function closeSocket(): void {
  if (socket) {
    socket.disconnect();
    console.log('🔄 Socket.IO desconectado por solicitud');
  }
}

// Subscripciones a eventos

// Evento de actualización de órdenes
export function subscribeToOrdersUpdate(callback: OrderUpdateCallback): () => void {
  const socket = getSocket();
  socket.on('orders_update', callback);
  return () => {
    socket.off('orders_update', callback);
  };
}

// Evento de orden eliminada
export function subscribeToOrderDeleted(callback: OrderDeletedCallback): () => void {
  const socket = getSocket();
  socket.on('order_deleted', (data) => {
    callback(data.id);
  });
  return () => {
    socket.off('order_deleted');
  };
}

// Evento de orden actualizada
export function subscribeToOrderUpdated(callback: OrderUpdatedCallback): () => void {
  const socket = getSocket();
  socket.on('order_updated', (data) => {
    callback(data.id, data.state);
  });
  return () => {
    socket.off('order_updated');
  };
}

// Evento de orden creada
export function subscribeToOrderCreated(callback: OrderCreatedCallback): () => void {
  const socket = getSocket();
  socket.on('order_created', (data) => {
    callback(data.id);
  });
  return () => {
    socket.off('order_created');
  };
}

// Evento de estado de conexión
export function subscribeToConnectionStatus(callback: ConnectionStatusCallback): () => void {
  const socket = getSocket();
  socket.on('connection_status', callback);
  return () => {
    socket.off('connection_status', callback);
  };
}

// Verificar estado del servidor
export async function checkServerStatus(): Promise<boolean> {
  try {
    const response = await fetch(`${SOCKET_URL}/api/orders/ws-status`);
    if (!response.ok) {
      console.error(`❌ Error al verificar estado del servidor: ${response.status} ${response.statusText}`);
      return false;
    }
    const data = await response.json();
    console.log('🔄 Estado del servidor WebSocket:', data);
    return data.websocket_status === 'active';
  } catch (error) {
    console.error('❌ Error al verificar estado del servidor:', error);
    return false;
  }
} 