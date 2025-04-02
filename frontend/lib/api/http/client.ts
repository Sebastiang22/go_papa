/**
 * Cliente HTTP para comunicación con el backend
 */
import { authService } from '../auth/authService';

// URL base del API, tomada de variables de entorno o valor por defecto
const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// Tipos de error de la API
interface ApiError {
  statusCode: number;
  message: string;
  details?: any;
}

/**
 * Opciones para la petición
 */
interface FetchOptions extends RequestInit {
  timeout?: number;
}

/**
 * Cliente HTTP mejorado con manejo de errores y timeout
 */
async function fetchWithTimeout(
  url: string,
  options: FetchOptions = {}
): Promise<Response> {
  const { timeout = 8000, ...fetchOptions } = options;
  
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    // Añadir token de autenticación si existe y no se especifica en las opciones
    if (!fetchOptions.headers || !('Authorization' in fetchOptions.headers)) {
      const token = authService.getAuthToken();
      if (token) {
        fetchOptions.headers = {
          ...fetchOptions.headers,
          'Authorization': `Bearer ${token}`
        };
      }
    }
    
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
    });
    
    if (!response.ok) {
      let errorData: ApiError;
      try {
        errorData = await response.json();
      } catch (e) {
        errorData = {
          statusCode: response.status,
          message: response.statusText || 'Error de servidor desconocido'
        };
      }
      
      // Si hay un error de autenticación (401), intentar cerrar sesión
      if (response.status === 401) {
        authService.logout();
      }
      
      throw new Error(errorData.message || `Error ${response.status}: ${response.statusText}`);
    }
    
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * API client con métodos para diferentes operaciones
 */
export const apiClient = {
  /**
   * Obtiene las órdenes del día
   */
  async getOrders() {
    const response = await fetchWithTimeout(`${API_URL}/orders/today`);
    return response.json();
  },
  
  /**
   * Actualiza el estado de una orden
   */
  async updateOrderStatus(orderId: string, newStatus: string) {
    const response = await fetchWithTimeout(`${API_URL}/orders/update_state`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        order_id: orderId,
        state: newStatus
      }),
    });
    
    return response.json();
  },
  
  /**
   * Elimina una orden
   */
  async deleteOrder(orderId: string) {
    const response = await fetchWithTimeout(`${API_URL}/orders/${orderId}`, {
      method: 'DELETE',
    });
    
    return response.json();
  },
  
  /**
   * Verifica el estado del servidor
   */
  async checkServerStatus() {
    try {
      const response = await fetchWithTimeout(`${API_URL}/api/orders/ws-status`, { 
        timeout: 3000 
      });
      return response.ok;
    } catch (error) {
      console.error('Error al verificar estado del servidor:', error);
      return false;
    }
  }
}; 