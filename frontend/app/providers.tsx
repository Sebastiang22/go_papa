"use client";

import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/toaster";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { Order, BackendData } from "@/lib/types/";
import { apiClient } from "@/lib/api/http/client";
import { AuthProvider, useAuth } from "@/lib/providers/auth-provider";

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

// Componente interno que accede al contexto de autenticación
function OrdersProviderWithAuth({ children }: OrdersProviderProps) {
  const { authState } = useAuth();
  const [backendData, setBackendData] = useState<BackendData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Función para cargar órdenes
  const refreshOrders = async () => {
    if (!authState.isAuthenticated) {
      console.log("No se cargan órdenes: usuario no autenticado");
      return;
    }
    
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
    if (!authState.isAuthenticated) return;
    
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
      
      // Actualizar datos después de la operación
      refreshOrders();
    } catch (err) {
      console.error("Error al actualizar estado:", err);
      // Recargar datos para revertir cambios optimistas incorrectos
      refreshOrders();
      throw err;
    }
  };

  // Eliminar una orden
  const deleteOrder = async (orderId: string) => {
    if (!authState.isAuthenticated) return;
    
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
      
      // Actualizar datos después de la operación
      refreshOrders();
    } catch (err) {
      console.error("Error al eliminar orden:", err);
      // Recargar datos para revertir cambios optimistas incorrectos
      refreshOrders();
      throw err;
    }
  };

  // Inicializar y cargar los datos cuando el usuario esté autenticado
  useEffect(() => {
    if (authState.isAuthenticated) {
      // Solo cargar órdenes si el usuario está autenticado
      refreshOrders();
    }
  }, [authState.isAuthenticated]);

  // Valor del contexto
  const value = {
    orders: backendData?.orders || [],
    stats: backendData?.stats || null,
    isLoading,
    error,
    lastUpdated,
    refreshOrders,
    updateOrderStatus,
    deleteOrder,
  };

  return <OrdersContext.Provider value={value}>{children}</OrdersContext.Provider>;
}

// Wrapper del proveedor de órdenes
export function OrdersProvider({ children }: OrdersProviderProps) {
  return (
    <OrdersProviderWithAuth>
      {children}
    </OrdersProviderWithAuth>
  );
}

// Proveedor principal que combina todos los proveedores
export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <AuthProvider>
        <OrdersProvider>
          {children}
          <Toaster />
        </OrdersProvider>
      </AuthProvider>
    </ThemeProvider>
  );
} 