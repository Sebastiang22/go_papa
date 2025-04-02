"use client";

import { useAuth } from "@/lib/providers/auth-provider";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const { authState, logout } = useAuth();
  const router = useRouter();
  
  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        
        <div className="flex items-center gap-4">
          <div className="text-right mr-4">
            <p className="font-medium">{authState.user?.name}</p>
            <p className="text-sm text-muted-foreground">{authState.user?.email}</p>
          </div>
          
          <Button 
            onClick={logout}
            variant="outline"
            size="sm"
          >
            Cerrar Sesión
          </Button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-card rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Órdenes</h2>
          <p className="text-muted-foreground">
            Gestione las órdenes de los restaurantes.
          </p>
          <Button 
            className="mt-4 w-full"
            onClick={() => router.push('/orders')}
          >
            Ver Órdenes
          </Button>
        </div>
        
        <div className="bg-card rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Inventario</h2>
          <p className="text-muted-foreground">
            Administre el inventario de los restaurantes.
          </p>
          <Button 
            className="mt-4 w-full"
            onClick={() => router.push('/inventory')}
          >
            Ver Inventario
          </Button>
        </div>
        
        <div className="bg-card rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Agentes IA</h2>
          <p className="text-muted-foreground">
            Configure los agentes inteligentes para los restaurantes.
          </p>
          <Button 
            className="mt-4 w-full"
            onClick={() => router.push('/agents')}
          >
            Gestionar Agentes
          </Button>
        </div>
      </div>
    </div>
  );
} 