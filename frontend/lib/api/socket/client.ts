/**
 * ESTE MÓDULO HA SIDO DESACTIVADO - TODAS LAS FUNCIONES AHORA SON DUMMY
 * Cliente WebSocket para comunicación en tiempo real
 */
// import { io, Socket } from 'socket.io-client';

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
let socket: any | null = null;

/**
 * Obtiene el socket (inicializándolo si es necesario)
 */
export function getSocket(): any {
  console.log('Socket.IO ha sido desactivado');
  return null;
}

/**
 * Inicializa la conexión Socket.IO con backoff exponencial
 */
export function initializeSocket(): void {
  console.log('Socket.IO ha sido desactivado');
  return;
}

/**
 * Cierra la conexión
 */
export function closeSocket(): void {
  console.log('Socket.IO ha sido desactivado');
  return;
}

// SUSCRIPCIONES A EVENTOS

/**
 * Suscripción a evento de actualización de órdenes
 */
export function subscribeToOrdersUpdate(callback: OrderUpdateCallback): () => void {
  console.log('Socket.IO ha sido desactivado');
  return () => {};
}

/**
 * Suscripción a evento de orden eliminada
 */
export function subscribeToOrderDeleted(callback: OrderDeletedCallback): () => void {
  console.log('Socket.IO ha sido desactivado');
  return () => {};
}

/**
 * Suscripción a evento de orden actualizada
 */
export function subscribeToOrderUpdated(callback: OrderUpdatedCallback): () => void {
  console.log('Socket.IO ha sido desactivado');
  return () => {};
}

/**
 * Suscripción a evento de orden creada
 */
export function subscribeToOrderCreated(callback: OrderCreatedCallback): () => void {
  console.log('Socket.IO ha sido desactivado');
  return () => {};
}

/**
 * Suscripción a evento de estado de conexión
 */
export function subscribeToConnectionStatus(callback: ConnectionStatusCallback): () => void {
  console.log('Socket.IO ha sido desactivado');
  return () => {};
}

/**
 * Verificar estado del servidor
 */
export async function checkServerStatus(): Promise<boolean> {
  return true;
} 