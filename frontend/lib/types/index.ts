/**
 * Tipos y interfaces para toda la aplicación
 */

/**
 * Representa un producto en un pedido
 */
export interface Product {
  name: string;
  quantity: number;
  price: number;
  observations?: string;
}

/**
 * Representa un pedido
 */
export interface Order {
  id: string;
  table_id: string;          // Dirección del cliente
  customer_name: string;     // Nombre del cliente
  products: Product[];       // Productos del pedido
  created_at: string;        // Fecha de creación
  updated_at: string;        // Fecha de actualización
  state: string;             // Estado: pendiente, en preparación, completado
  enum_order_table?: string; // Identificador adicional de la orden
}

/**
 * Datos recibidos del backend
 */
export interface BackendData {
  stats: {
    total_orders: number;
    pending_orders: number;
    complete_orders: number;
    total_sales: number;
  };
  orders: Order[];
}

/**
 * Estados de una orden
 */
export enum OrderState {
  PENDING = 'pendiente',
  PREPARING = 'en preparación',
  COMPLETED = 'completado'
}

/**
 * Tipo para las funciones de callback de órdenes
 */
export type OrderCallback = (order: Order) => void;
export type OrderStatusCallback = (orderId: string, newStatus: string) => Promise<void>;
export type OrderDeleteCallback = (orderId: string) => void; 