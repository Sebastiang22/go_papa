"use client";

import { useAuth } from "@/lib/providers/auth-provider";
import { useRouter } from "next/navigation";
import { useEffect, ReactNode } from "react";
import { Spinner } from "@/components/ui/spinner";

interface ProtectedRouteProps {
  children: ReactNode;
  fallbackUrl?: string;
}

/**
 * Componente para proteger rutas que requieren autenticación.
 * 
 * Si el usuario no está autenticado, redirige a la página especificada
 * en fallbackUrl (por defecto '/').
 */
export default function ProtectedRoute({ 
  children, 
  fallbackUrl = '/' 
}: ProtectedRouteProps) {
  const { authState } = useAuth();
  const router = useRouter();
  
  useEffect(() => {
    // Si la carga ha terminado y el usuario no está autenticado
    if (!authState.isLoading && !authState.isAuthenticated) {
      router.push(fallbackUrl);
    }
  }, [authState.isAuthenticated, authState.isLoading, router, fallbackUrl]);
  
  // Mientras se verifica la autenticación, mostrar indicador de carga
  if (authState.isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <Spinner size="lg" />
          <p className="text-lg text-muted-foreground">Verificando autenticación...</p>
        </div>
      </div>
    );
  }
  
  // Si está autenticado, mostrar el contenido protegido
  return authState.isAuthenticated ? <>{children}</> : null;
} 