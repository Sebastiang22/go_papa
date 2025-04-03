"use client";

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from "react";
import { useRouter } from "next/navigation";

// URL base del API, tomada de variables de entorno o valor por defecto
const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// Tipo de datos para el estado de autenticación
interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: {
    name: string;
    email: string;
  } | null;
  error: string | null;
}

// Tipo de datos para el contexto de autenticación
interface AuthContextType {
  authState: AuthState;
  login: () => void;
  logout: () => void;
  verifyToken: () => Promise<boolean>;
}

// Crear el contexto con valores por defecto
const AuthContext = createContext<AuthContextType>({
  authState: {
    isAuthenticated: false,
    isLoading: true,
    user: null,
    error: null,
  },
  login: () => {},
  logout: () => {},
  verifyToken: async () => false,
});

// Hook para usar el contexto de autenticación
export const useAuth = () => useContext(AuthContext);

// Proveedor de autenticación
interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    user: null,
    error: null,
  });
  
  const router = useRouter();
  
  // Verificar token al cargar la página
  useEffect(() => {
    const tokenFromQuery = new URLSearchParams(window.location.search).get('token');
    
    // Si hay un token en la URL, guardarlo en el almacenamiento local
    if (tokenFromQuery) {
      // Eliminar token de la URL para evitar que se comparta accidentalmente
      const newUrl = window.location.pathname;
      window.history.replaceState({}, document.title, newUrl);
      
      // Verificar token
      verifyToken();
    } else {
      // Verificar token almacenado en cookie (esto se manejará desde el backend)
      verifyToken();
    }
  }, []);
  
  // Función para verificar la validez del token
  const verifyToken = useCallback(async (): Promise<boolean> => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));
      
      const response = await fetch(`${API_URL}/auth/verify-token`, {
        method: 'GET',
        credentials: 'include', // Importante: enviar cookies con la solicitud
      });
      
      const data = await response.json();
      
      if (response.ok && data.isValid) {
        setAuthState({
          isAuthenticated: true,
          isLoading: false,
          user: data.user,
          error: null,
        });
        return true;
      } else {
        setAuthState({
          isAuthenticated: false,
          isLoading: false,
          user: null,
          error: data.error || 'Error al verificar la autenticación',
        });
        return false;
      }
    } catch (error) {
      setAuthState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        error: 'Error de conexión al servidor de autenticación',
      });
      return false;
    }
  }, []);
  
  // Función para iniciar sesión
  const login = useCallback(() => {
    window.location.href = `${API_URL}/auth/login`;
  }, []);
  
  // Función para cerrar sesión
  const logout = useCallback(async () => {
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: 'GET',
        credentials: 'include',
      });
      
      setAuthState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        error: null,
      });
      
      router.push('/');
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
      // Cerrar sesión localmente incluso si hay un error en el servidor
      setAuthState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        error: 'Error al cerrar sesión',
      });
      router.push('/');
    }
  }, [router]);
  
  // Valor del contexto
  const value = {
    authState,
    login,
    logout,
    verifyToken,
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
} 