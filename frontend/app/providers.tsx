"use client";

import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/toaster";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { Order, BackendData } from "@/lib/types";
import { apiClient } from "@/lib/api/http/client";
import {
  subscribeToOrdersUpdate,
  subscribeToOrderDeleted,
  subscribeToOrderUpdated,
  subscribeToOrderCreated,
  initializeSocket,
  closeSocket
} from "@/lib/api/socket/client";

// Interfaz del contexto de órdenes
interface OrdersContextType {
  orders: Order[];
  stats: {
    total_orders: number;
    pending_orders: number;
    complete_orders: number;
    total_sales: number;
  } | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  isConnected: boolean;
  clientCount: number;
  refreshOrders: () => Promise<void>;
  updateOrderStatus: (orderId: string, newStatus: string) => Promise<void>;
  deleteOrder: (orderId: string) => Promise<void>;
}

// Crear el contexto con valores por defecto
const OrdersContext = createContext<OrdersContextType>({
  orders: [],
  stats: null,
  isLoading: false,
  error: null,
  lastUpdated: null,
  isConnected: false,
  clientCount: 0,
  refreshOrders: async () => {},
  updateOrderStatus: async () => {},
  deleteOrder: async () => {},
});

// Hook para usar el contexto de órdenes
export const useOrders = () => useContext(OrdersContext);

// Proveedor de órdenes
interface OrdersProviderProps {
  children: ReactNode;
}

export function OrdersProvider({ children }: OrdersProviderProps) {
  const [backendData, setBackendData] = useState<BackendData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [clientCount, setClientCount] = useState<number>(0);

  // Función para cargar órdenes
  const refreshOrders = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const data = await apiClient.getOrders();
      
      setBackendData(data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Error al obtener órdenes:", err);
      setError(err instanceof Error ? err.message : "Error al cargar órdenes");
    } finally {
      setIsLoading(false);
    }
  };

  // Actualizar el estado de una orden
  const updateOrderStatus = async (orderId: string, newStatus: string) => {
    try {
      await apiClient.updateOrderStatus(orderId, newStatus);
      
      // Actualización optimista
      if (backendData) {
        const updatedOrders = backendData.orders.map(order => {
          if (order.id === orderId) {
            return { ...order, state: newStatus };
          }
          return order;
        });
        
        // Actualizar estadísticas
        const statsUpdate = { ...backendData.stats };
        // Lógica para actualizar estadísticas basadas en el cambio de estado...
        
        setBackendData({
          ...backendData,
          orders: updatedOrders,
          stats: statsUpdate
        });
      }
    } catch (err) {
      console.error("Error al actualizar estado:", err);
      // Recargar datos para revertir cambios optimistas incorrectos
      refreshOrders();
      throw err;
    }
  };

  // Eliminar una orden
  const deleteOrder = async (orderId: string) => {
    try {
      await apiClient.deleteOrder(orderId);
      
      // Actualización optimista
      if (backendData) {
        const updatedOrders = backendData.orders.filter(order => order.id !== orderId);
        
        setBackendData({
          ...backendData,
          orders: updatedOrders,
          // Actualizar estadísticas...
        });
      }
    } catch (err) {
      console.error("Error al eliminar orden:", err);
      // Recargar datos para revertir cambios optimistas incorrectos
      refreshOrders();
      throw err;
    }
  };

  // Inicializar websockets y suscripciones
  useEffect(() => {
    // Inicializar socket
    initializeSocket();
    
    // Suscribirse a eventos
    const unsubscribeOrdersUpdate = subscribeToOrdersUpdate(() => {
      refreshOrders();
    });
    
    const unsubscribeOrderDeleted = subscribeToOrderDeleted((orderId) => {
      // Actualización optimista
      if (backendData) {
        const updatedOrders = backendData.orders.filter(order => order.id !== orderId);
        setBackendData({
          ...backendData,
          orders: updatedOrders,
        });
      }
      refreshOrders(); // Actualizar datos completos
    });
    
    const unsubscribeOrderUpdated = subscribeToOrderUpdated((orderId, newState) => {
      // Actualización optimista
      if (backendData) {
        const updatedOrders = backendData.orders.map(order => {
          if (order.id === orderId) {
            return { ...order, state: newState };
          }
          return order;
        });
        setBackendData({
          ...backendData,
          orders: updatedOrders,
        });
      }
      refreshOrders(); // Actualizar datos completos
    });
    
    const unsubscribeOrderCreated = subscribeToOrderCreated(() => {
      refreshOrders(); // Actualizar datos completos
    });
    
    // Cargar órdenes iniciales
    refreshOrders();
    
    // Limpiar suscripciones al desmontar
    return () => {
      unsubscribeOrdersUpdate();
      unsubscribeOrderDeleted();
      unsubscribeOrderUpdated();
      unsubscribeOrderCreated();
      closeSocket();
    };
  }, []);

  // Valor del contexto
  const value = {
    orders: backendData?.orders || [],
    stats: backendData?.stats || null,
    isLoading,
    error,
    lastUpdated,
    isConnected,
    clientCount,
    refreshOrders,
    updateOrderStatus,
    deleteOrder,
  };

  return <OrdersContext.Provider value={value}>{children}</OrdersContext.Provider>;
}

// Proveedor principal que combina todos los proveedores
export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <OrdersProvider>
        {children}
        <Toaster />
      </OrdersProvider>
    </ThemeProvider>
  );
} 