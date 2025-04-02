import { useState, useEffect, useCallback } from 'react';
import { Order } from '@/components/order-list';

interface UseRealTimeOrdersProps {
  onOrderDeleted?: (orderId: string) => void;
  onOrderUpdated?: (orderId: string, newState: string) => void;
  onOrderCreated?: (orderId: string) => void;
}

interface UseRealTimeOrdersReturn {
  isConnected: boolean;
  clientCount: number;
  lastUpdated: Date | null;
  orders: Order[] | null;
  stats: {
    total: number;
    pending: number;
    inProgress: number;
    completed: number;
    cancelled: number;
  };
  error: string | null;
  fetchData: () => Promise<void>;
  isLoading: boolean;
}

export function useRealTimeOrders({
  onOrderDeleted: externalOrderDeletedHandler,
  onOrderUpdated: externalOrderUpdatedHandler,
  onOrderCreated: externalOrderCreatedHandler,
}: UseRealTimeOrdersProps = {}): UseRealTimeOrdersReturn {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [clientCount, setClientCount] = useState<number>(0);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [orders, setOrders] = useState<Order[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    inProgress: 0,
    completed: 0,
    cancelled: 0
  });

  // Función para calcular estadísticas
  const calculateStats = useCallback((orders: Order[]) => {
    return {
      total: orders.length,
      pending: orders.filter(order => order.state === 'pending').length,
      inProgress: orders.filter(order => order.state === 'in_progress').length,
      completed: orders.filter(order => order.state === 'completed').length,
      cancelled: orders.filter(order => order.state === 'cancelled').length
    };
  }, []);

  // Función para obtener datos
  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch('/api/orders');
      if (!response.ok) {
        throw new Error(`Error al obtener órdenes: ${response.statusText}`);
      }
      
      const data = await response.json();
      setOrders(data);
      setStats(calculateStats(data));
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error al obtener órdenes:', err);
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setIsLoading(false);
    }
  }, [calculateStats]);

  // Efecto para inicializar y mantener actualizados los datos
  useEffect(() => {
    console.log('🔄 Inicializando sistema de actualización manual...');
    
    // Cargar datos iniciales
    fetchData();
    
    // Configurar actualización periódica cada 30 segundos
    const intervalId = setInterval(() => {
      console.log('🔄 Actualización periódica de datos...');
      fetchData();
    }, 30000);
    
    // Limpieza al desmontar
    return () => {
      console.log('🧹 Limpiando sistema de actualización...');
      clearInterval(intervalId);
    };
  }, [fetchData]);

  return {
    isConnected,
    clientCount,
    lastUpdated,
    orders,
    stats,
    error,
    fetchData,
    isLoading
  };
} 