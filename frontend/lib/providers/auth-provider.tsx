"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { User, AuthState } from "@/lib/types/auth";
import { authService } from "@/lib/api/auth/authService";
import { useRouter } from "next/navigation";

// Contexto de autenticación
const AuthContext = createContext<{
  authState: AuthState;
  login: () => void;
  logout: () => void;
}>({
  authState: {
    user: null,
    token: null,
    expiresAt: null,
    isAuthenticated: false,
    isLoading: true,
    error: null
  },
  login: () => {},
  logout: () => {},
});

export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    expiresAt: null,
    isAuthenticated: false,
    isLoading: true,
    error: null
  });
  
  const router = useRouter();
  
  // Verificar estado de autenticación al iniciar
  useEffect(() => {
    // Verificar si hay parámetros de autenticación en la URL (redirección desde el flujo de login)
    const authResult = authService.handleAuthCallback();
    
    if (authResult.success && authResult.user && authResult.token) {
      setAuthState({
        user: authResult.user,
        token: authResult.token,
        expiresAt: Date.now() + (authResult.expiresIn || 3600) * 1000,
        isAuthenticated: true,
        isLoading: false,
        error: null
      });
    } else {
      // Si no hay parámetros en la URL, verificar si hay una sesión guardada
      const isAuthenticated = authService.isAuthenticated();
      
      if (isAuthenticated) {
        const user = authService.getCurrentUser();
        const token = authService.getAuthToken();
        
        setAuthState({
          user,
          token,
          expiresAt: null, // No necesitamos establecerlo aquí, se maneja internamente
          isAuthenticated: true,
          isLoading: false,
          error: null
        });
      } else {
        // No hay sesión activa
        setAuthState(prev => ({
          ...prev,
          isLoading: false,
          isAuthenticated: false
        }));
      }
    }
  }, []);
  
  // Iniciar sesión
  const login = () => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      authService.login();
      // No actualizamos el estado ya que se redirigirá a Microsoft
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: 'Error al iniciar el proceso de autenticación'
      }));
    }
  };
  
  // Cerrar sesión
  const logout = () => {
    authService.logout();
    setAuthState({
      user: null,
      token: null,
      expiresAt: null,
      isAuthenticated: false,
      isLoading: false,
      error: null
    });
    router.push('/');
  };
  
  return (
    <AuthContext.Provider value={{ authState, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
} 