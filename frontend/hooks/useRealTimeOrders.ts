import { useState, useEffect, useCallback } from 'react';
import {
  getSocket,
  initializeSocket,
  closeSocket,
  subscribeToOrdersUpdate,
  subscribeToOrderDeleted,
  subscribeToOrderUpdated,
  subscribeToOrderCreated,
  subscribeToConnectionStatus,
  checkServerStatus
} from '../lib/socketClient';
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
    preparing: number;
    ready: number;
    delivered: number;
    cancelled: number;
  } | null;
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
  const [stats, setStats] = useState<{
    total: number;
    pending: number;
    preparing: number;
    ready: number;
    delivered: number;
    cancelled: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  // Función para calcular estadísticas basadas en órdenes
  const calculateStats = useCallback((orderList: Order[]): {
    total: number;
    pending: number;
    preparing: number;
    ready: number;
    delivered: number;
    cancelled: number;
  } => {
    const newStats = {
      total: orderList.length,
      pending: 0,
      preparing: 0,
      ready: 0,
      delivered: 0,
      cancelled: 0
    };

    orderList.forEach(order => {
      const state = order.state?.toLowerCase() || 'pending';
      if (newStats.hasOwnProperty(state)) {
        newStats[state as keyof typeof newStats]++;
      }
    });

    return newStats;
  }, []);

  // Función para obtener datos
  const fetchData = useCallback(async () => {
    try {
      console.log('🔄 Obteniendo datos de órdenes...');
      setIsLoading(true);
      setError(null);
      
      const response = await fetch(`${API_URL}/orders/today`);
      
      if (response.status === 404) {
        console.log('⚠️ No se encontraron órdenes');
        setOrders([]);
        setStats({
          total: 0,
          pending: 0,
          preparing: 0,
          ready: 0,
          delivered: 0,
          cancelled: 0
        });
        setLastUpdated(new Date());
        return;
      }
      
      if (!response.ok) {
        throw new Error(`Error al obtener órdenes: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      setOrders(data.orders || []);
      setStats(calculateStats(data.orders || []));
      setLastUpdated(new Date());
      
      console.log(`✅ Datos cargados: ${data.orders?.length || 0} órdenes`);
    } catch (err) {
      console.error('❌ Error en fetchData:', err);
      setError(err instanceof Error ? err.message : 'Error al obtener datos');
    } finally {
      setIsLoading(false);
    }
  }, [calculateStats, API_URL]);

  // Efecto para inicializar conexión WebSocket
  useEffect(() => {
    console.log('🔄 Inicializando conexión WebSocket...');
    
    // Intentar inicializar el socket directamente
    initializeSocket();
    
    // Funciones de manejo de eventos
    const handleConnect = () => {
      console.log('✅ Conectado al servidor WebSocket');
      setIsConnected(true);
      setError(null);
      fetchData();
    };
    
    const handleDisconnect = (reason: string) => {
      console.log(`❌ Desconectado del servidor WebSocket: ${reason}`);
      setIsConnected(false);
      if (reason === 'io server disconnect') {
        // Si el servidor cerró la conexión, intentamos reconectar
        getSocket().connect();
      }
    };
    
    const handleConnectionStatus = (data: { status: string; sid?: string; clients: number }) => {
      console.log('🔄 Estado de conexión actualizado:', data);
      setClientCount(data.clients);
      setIsConnected(data.status === 'connected');
    };
    
    // Registrar callbacks para eventos
    const socket = getSocket();
    
    // Conexión y desconexión
    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);
    
    // Manejar errores de conexión
    socket.on('connect_error', (error) => {
      console.error('❌ Error de conexión:', error);
      setError(`Error de conexión: ${error.message}`);
    });
    
    // Suscripción a eventos
    const unsubscribeOrdersUpdate = subscribeToOrdersUpdate(() => {
      console.log('🔄 Actualización de órdenes recibida');
      fetchData();
    });
    
    const unsubscribeOrderDeleted = subscribeToOrderDeleted((orderId) => {
      console.log(`🗑️ Orden eliminada: ${orderId}`);
      setOrders(prevOrders => {
        // Actualización optimista para UI más responsive
        const updatedOrders = prevOrders?.filter(order => 
          order?.id !== orderId && order?.enum_order_table !== orderId
        );
        setStats(calculateStats(updatedOrders || []));
        return updatedOrders;
      });
      fetchData(); // Sincronizar con el servidor después
    });
    
    const unsubscribeOrderUpdated = subscribeToOrderUpdated((orderId, newState) => {
      console.log(`🔄 Orden actualizada: ${orderId} -> ${newState}`);
      setOrders(prevOrders => {
        // Actualización optimista para UI más responsive
        const updatedOrders = prevOrders?.map(order => {
          if (order?.id === orderId || order?.enum_order_table === orderId) {
            return { ...order, state: newState };
          }
          return order;
        });
        setStats(calculateStats(updatedOrders || []));
        return updatedOrders;
      });
      fetchData(); // Sincronizar con el servidor después
    });
    
    const unsubscribeOrderCreated = subscribeToOrderCreated((orderId) => {
      console.log(`✨ Nueva orden creada: ${orderId}`);
      fetchData(); // Cargar la orden nueva
    });
    
    // Suscribirse al estado de la conexión
    const unsubscribeConnectionStatus = subscribeToConnectionStatus(handleConnectionStatus);
    
    // Cargar datos iniciales, incluso sin conexión
    fetchData();
    
    // Verificar estado del servidor periódicamente
    const intervalId = setInterval(() => {
      if (!isConnected) {
        checkServerStatus().then(isActive => {
          if (isActive && !isConnected) {
            console.log('🔄 Servidor WebSocket disponible, reconectando...');
            getSocket().connect();
          }
        });
      }
    }, 10000); // Comprobar cada 10 segundos
    
    // Limpieza al desmontar
    return () => {
      console.log('🧹 Limpiando suscripciones WebSocket...');
      
      // Eliminar listeners de conexión
      socket.off('connect', handleConnect);
      socket.off('disconnect', handleDisconnect);
      socket.off('connect_error');
      
      // Cancelar suscripciones
      if (typeof unsubscribeOrdersUpdate === 'function') unsubscribeOrdersUpdate();
      if (typeof unsubscribeOrderDeleted === 'function') unsubscribeOrderDeleted();
      if (typeof unsubscribeOrderUpdated === 'function') unsubscribeOrderUpdated();
      if (typeof unsubscribeOrderCreated === 'function') unsubscribeOrderCreated();
      if (typeof unsubscribeConnectionStatus === 'function') unsubscribeConnectionStatus();
      
      // Limpiar intervalo
      clearInterval(intervalId);
      
      // Cerrar socket
      closeSocket();
    };
  }, [fetchData, calculateStats, isConnected]);

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