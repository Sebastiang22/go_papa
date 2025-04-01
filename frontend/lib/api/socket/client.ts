/**
 * Cliente WebSocket para comunicación en tiempo real
 */
import { io, Socket } from 'socket.io-client';

// Tipos para los callbacks
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

// Variable global para mantener una única instancia del socket
let socket: Socket | null = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

// URL del servidor Socket.IO
const SOCKET_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// Opciones mejoradas de conexión
const socketOptions = {
  autoConnect: true,
  reconnectionAttempts: MAX_RECONNECT_ATTEMPTS,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  randomizationFactor: 0.5,
  timeout: 20000,
  transports: ['websocket', 'polling'],
  path: '/api/socket.io/'
};

/**
 * Obtiene el socket (inicializándolo si es necesario)
 */
export function getSocket(): Socket {
  if (!socket) {
    console.log('🔄 Inicializando Socket.IO...');
    initializeSocket();
  }
  return socket!;
}

/**
 * Inicializa la conexión Socket.IO con backoff exponencial
 */
export function initializeSocket(): void {
  if (socket) {
    if (!socket.connected) {
      console.log('🔄 Socket no conectado, reconectando...');
      socket.connect();
    }
    return;
  }

  try {
    console.log(`🔄 Conectando a: ${SOCKET_URL}`);
    socket = io(SOCKET_URL, socketOptions);

    // Eventos de conexión
    socket.on('connect', () => {
      console.log(`✅ Socket.IO conectado: ${socket?.id}`);
      reconnectAttempts = 0;
    });

    socket.on('disconnect', (reason) => {
      console.log(`❌ Socket.IO desconectado: ${reason}`);
    });

    socket.on('reconnect', (attempt) => {
      console.log(`🔄 Socket.IO reconectado después de ${attempt} intentos`);
      reconnectAttempts = 0;
    });

    socket.on('reconnect_attempt', (attempt) => {
      const delay = Math.min(1000 * Math.pow(1.5, attempt), 10000); // Backoff exponencial
      console.log(`🔄 Socket.IO intento de reconexión #${attempt} (espera: ${delay}ms)`);
      reconnectAttempts = attempt;
    });

    socket.on('reconnect_error', (error) => {
      console.error(`❌ Error de reconexión Socket.IO:`, error);
    });

    socket.on('reconnect_failed', () => {
      console.error(`❌ Reconexión Socket.IO fallida después de ${MAX_RECONNECT_ATTEMPTS} intentos`);
    });

    socket.on('error', (error) => {
      console.error(`❌ Error Socket.IO:`, error);
    });

    socket.on('connect_error', (error) => {
      console.error(`❌ Error de conexión Socket.IO:`, error);
    });

  } catch (error) {
    console.error('❌ Error al inicializar Socket.IO:', error);
  }
}

/**
 * Cierra la conexión
 */
export function closeSocket(): void {
  if (socket) {
    socket.disconnect();
    console.log('🔄 Socket.IO desconectado por solicitud');
  }
}

// SUSCRIPCIONES A EVENTOS

/**
 * Suscripción a evento de actualización de órdenes
 */
export function subscribeToOrdersUpdate(callback: OrderUpdateCallback): () => void {
  const socket = getSocket();
  
  const handler = () => {
    console.log('🔄 Actualización de órdenes recibida');
    callback();
  };
  
  socket.on('orders_update', handler);
  
  return () => {
    socket.off('orders_update', handler);
  };
}

/**
 * Suscripción a evento de orden eliminada
 */
export function subscribeToOrderDeleted(callback: OrderDeletedCallback): () => void {
  const socket = getSocket();
  
  const handler = (data: {id: string}) => {
    console.log(`🗑️ Orden eliminada: ${data.id}`);
    callback(data.id);
  };
  
  socket.on('order_deleted', handler);
  
  return () => {
    socket.off('order_deleted', handler);
  };
}

/**
 * Suscripción a evento de orden actualizada
 */
export function subscribeToOrderUpdated(callback: OrderUpdatedCallback): () => void {
  const socket = getSocket();
  
  const handler = (data: {id: string, state: string}) => {
    console.log(`🔄 Orden actualizada: ${data.id} -> ${data.state}`);
    callback(data.id, data.state);
  };
  
  socket.on('order_updated', handler);
  
  return () => {
    socket.off('order_updated', handler);
  };
}

/**
 * Suscripción a evento de orden creada
 */
export function subscribeToOrderCreated(callback: OrderCreatedCallback): () => void {
  const socket = getSocket();
  
  const handler = (data: {id: string}) => {
    console.log(`✨ Orden creada: ${data.id}`);
    callback(data.id);
  };
  
  socket.on('order_created', handler);
  
  return () => {
    socket.off('order_created', handler);
  };
}

/**
 * Suscripción a evento de estado de conexión
 */
export function subscribeToConnectionStatus(callback: ConnectionStatusCallback): () => void {
  const socket = getSocket();
  
  const handler = (status: { status: string; sid?: string; clients: number }) => {
    console.log('🔄 Estado de conexión:', status);
    callback(status);
  };
  
  socket.on('connection_status', handler);
  
  return () => {
    socket.off('connection_status', handler);
  };
}

/**
 * Verificar estado del servidor
 */
export async function checkServerStatus(): Promise<boolean> {
  try {
    const socketConnected = socket?.connected || false;
    if (socketConnected) {
      return true;
    }
    
    // Si el socket no está conectado, verificar mediante una solicitud HTTP
    const response = await fetch(`${SOCKET_URL}/api/orders/ws-status`, {
      signal: AbortSignal.timeout(3000), // Timeout de 3 segundos
    });
    
    return response.ok;
  } catch (error) {
    console.error(`❌ Error al verificar estado del servidor:`, error);
    return false;
  }
} 