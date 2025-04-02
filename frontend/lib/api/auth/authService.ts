/**
 * Servicio de autenticación
 */
import { User, TokenValidationResult } from '@/lib/types/auth';

// URL base del API, tomada de variables de entorno o valor por defecto
const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * Clase de gestión de tokens de autenticación
 */
export class TokenManager {
  // Claves para almacenamiento local
  private static readonly TOKEN_KEY = 'auth_token';
  private static readonly USER_KEY = 'auth_user';
  private static readonly EXPIRES_AT_KEY = 'auth_expires_at';

  /**
   * Guarda el token de autenticación y datos relacionados
   */
  static saveToken(token: string, expiresIn: number, user: User): void {
    if (typeof window === 'undefined') return;
    
    const expiresAt = Date.now() + expiresIn * 1000;
    
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    localStorage.setItem(this.EXPIRES_AT_KEY, expiresAt.toString());
  }

  /**
   * Obtiene el token almacenado
   */
  static getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Obtiene el usuario almacenado
   */
  static getUser(): User | null {
    if (typeof window === 'undefined') return null;
    
    const userJson = localStorage.getItem(this.USER_KEY);
    if (!userJson) return null;
    
    try {
      return JSON.parse(userJson) as User;
    } catch (e) {
      console.error('Error al parsear datos de usuario:', e);
      return null;
    }
  }

  /**
   * Obtiene el tiempo de expiración del token
   */
  static getExpiresAt(): number | null {
    if (typeof window === 'undefined') return null;
    
    const expiresAt = localStorage.getItem(this.EXPIRES_AT_KEY);
    return expiresAt ? parseInt(expiresAt) : null;
  }

  /**
   * Verifica si el token ha expirado
   */
  static isTokenExpired(): boolean {
    const expiresAt = this.getExpiresAt();
    if (!expiresAt) return true;
    
    // Considerar el token expirado 5 minutos antes para evitar problemas
    return Date.now() > expiresAt - 5 * 60 * 1000;
  }

  /**
   * Elimina toda la información de autenticación almacenada
   */
  static clearToken(): void {
    if (typeof window === 'undefined') return;
    
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    localStorage.removeItem(this.EXPIRES_AT_KEY);
  }
}

/**
 * Servicio de autenticación para la aplicación
 */
export const authService = {
  /**
   * Inicia sesión redirigiendo al usuario a Microsoft
   */
  login(): void {
    window.location.href = `${API_URL}/auth/login`;
  },
  
  /**
   * Procesa parámetros de URL después de una redirección de autenticación
   */
  handleAuthCallback(): { success: boolean; user?: User; token?: string; expiresIn?: number } {
    if (typeof window === 'undefined') return { success: false };
    
    const params = new URLSearchParams(window.location.search);
    const name = params.get('name');
    const email = params.get('email');
    const token = params.get('token');
    const expiresIn = params.get('expires_in');
    
    if (name && email && token && expiresIn) {
      const user: User = { name, email };
      const expiresInSeconds = parseInt(expiresIn);
      
      // Guardar datos de autenticación
      TokenManager.saveToken(token, expiresInSeconds, user);
      
      // Limpiar parámetros de URL
      window.history.replaceState({}, document.title, window.location.pathname);
      
      return { 
        success: true, 
        user,
        token,
        expiresIn: expiresInSeconds
      };
    }
    
    return { success: false };
  },
  
  /**
   * Verifica si hay una sesión de usuario activa
   */
  isAuthenticated(): boolean {
    const token = TokenManager.getToken();
    const user = TokenManager.getUser();
    
    if (!token || !user) return false;
    
    return !TokenManager.isTokenExpired();
  },
  
  /**
   * Obtiene los datos del usuario actual
   */
  getCurrentUser(): User | null {
    if (!this.isAuthenticated()) return null;
    return TokenManager.getUser();
  },
  
  /**
   * Obtiene el token actual para solicitudes API
   */
  getAuthToken(): string | null {
    if (!this.isAuthenticated()) return null;
    return TokenManager.getToken();
  },
  
  /**
   * Valida un token con el backend
   */
  async validateToken(token: string): Promise<TokenValidationResult> {
    try {
      const response = await fetch(`${API_URL}/auth/validate-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });
      
      return await response.json();
    } catch (error) {
      console.error('Error al validar token:', error);
      return { valid: false, error: 'Error de conexión al validar token' };
    }
  },
  
  /**
   * Cierra la sesión del usuario
   */
  logout(): void {
    TokenManager.clearToken();
    // Opcional: redireccionar a página de inicio
    window.location.href = '/';
  }
}; 