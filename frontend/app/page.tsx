"use client";

import { useAuth } from "@/lib/providers/auth-provider";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { LoginButton } from "@/components/auth/login-button";
import { useEffect, useState } from "react";
import { Spinner } from "@/components/ui/spinner";

export default function HomePage() {
  const { authState, login } = useAuth();
  const router = useRouter();
  const [isRedirecting, setIsRedirecting] = useState(false);
  
  // Redirigir al dashboard si ya está autenticado
  useEffect(() => {
    if (authState.isAuthenticated && !authState.isLoading) {
      setIsRedirecting(true);
      router.push('/dashboard');
    }
  }, [authState.isAuthenticated, authState.isLoading, router]);
  
  // Mostrar indicador de carga mientras se verifica autenticación o redirección
  if (authState.isLoading || isRedirecting) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <Spinner size="lg" />
          <p className="text-lg text-muted-foreground">
            {isRedirecting ? "Redirigiendo al dashboard..." : "Cargando..."}
          </p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <h1 className="text-4xl font-bold mb-2">Bienvenido</h1>
      <p className="text-xl text-muted-foreground mb-8 text-center max-w-md">
        Sistema de gestión de restaurantes con inteligencia artificial
      </p>
      
      {authState.isAuthenticated ? (
        <div className="flex flex-col items-center gap-4">
          <div className="text-center mb-4">
            <p className="font-medium">Sesión iniciada como:</p>
            <p className="text-lg font-bold">{authState.user?.name}</p>
            <p className="text-sm text-muted-foreground">{authState.user?.email}</p>
          </div>
          
          <Button 
            onClick={() => {
              setIsRedirecting(true);
              router.push('/dashboard');
            }}
            size="lg"
            className="min-w-[200px]"
          >
            Ir al Dashboard
          </Button>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-6">
          <p className="text-center text-muted-foreground mb-2">
            Inicia sesión para acceder al sistema
          </p>
          
          <LoginButton 
            size="lg"
            className="min-w-[240px]"
          />
        </div>
      )}
    </div>
  );
}

