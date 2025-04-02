/**
 * Tipos relacionados con la autenticación en la aplicación
 */

/**
 * Información del usuario autenticado
 */
export interface User {
  /** Nombre completo del usuario */
  name: string;
  
  /** Correo electrónico del usuario */
  email: string;
  
  /** Roles o permisos del usuario (opcional) */
  roles?: string[];
}

/**
 * Estado de autenticación
 */
export interface AuthState {
  /** Usuario autenticado (null si no hay sesión) */
  user: User | null;
  
  /** Token de acceso para API calls */
  token: string | null;
  
  /** Timestamp de expiración del token */
  expiresAt: number | null;
  
  /** Indica si el usuario está autenticado */
  isAuthenticated: boolean;
  
  /** Indica si se está procesando alguna operación de autenticación */
  isLoading: boolean;
  
  /** Error de autenticación si existe */
  error: string | null;
}

/**
 * Respuesta del proceso de inicio de sesión
 */
export interface LoginResponse {
  /** Éxito del inicio de sesión */
  success: boolean;
  
  /** Mensaje de éxito o error */
  message?: string;
  
  /** Datos del usuario si el inicio de sesión fue exitoso */
  user?: User;
  
  /** Token de acceso si el inicio de sesión fue exitoso */
  token?: string;
  
  /** Tiempo de expiración del token en segundos */
  expiresIn?: number;
}

/**
 * Resultado de la validación de un token
 */
export interface TokenValidationResult {
  /** Indica si el token es válido */
  valid: boolean;
  
  /** Nombre del usuario asociado al token */
  name?: string;
  
  /** Correo del usuario asociado al token */
  email?: string;
  
  /** Mensaje de error si el token es inválido */
  error?: string;
} 