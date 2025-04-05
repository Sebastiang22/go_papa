"use client";

import { useState, useCallback } from "react";
import { OrdersList } from "./orders/order-list";
import { OrderModal } from "./orders/order-modal";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { Statistics } from "./stats/statistics";
import { useOrders } from "@/app/providers";
import { useToast } from "@/components/ui/use-toast";
import { LogOut, MoonIcon, SunIcon, User } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/lib/providers/auth-provider";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import type { Order } from "@/lib/types";

// Componente Emoji accesible
const Emoji = ({ 
  symbol, 
  label, 
  className 
}: { 
  symbol: string; 
  label?: string; 
  className?: string 
}) => (
  <span
    className={`emoji ${className || ""}`}
    role="img"
    aria-label={label || ""}
    aria-hidden={label ? "false" : "true"}
  >
    {symbol}
  </span>
);

/**
 * Componente principal del Dashboard
 */
export function DashboardClient() {
  const { theme, setTheme } = useTheme();
  const { toast } = useToast();
  const { authState, logout } = useAuth();
  const { 
    orders, 
    stats, 
    isLoading, 
    error, 
    refreshOrders, 
    updateOrderStatus, 
    deleteOrder 
  } = useOrders();

  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false);
  const [pendingDeleteOrderId, setPendingDeleteOrderId] = useState<string | null>(null);
  const [updatingOrderIds, setUpdatingOrderIds] = useState<Set<string>>(new Set());

  // Obtener las iniciales para el avatar
  const getUserInitials = () => {
    if (!authState.user?.name) return "U";
    return authState.user.name
      .split(" ")
      .map(part => part[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  // Manejar cerrar sesión
  const handleLogout = () => {
    try {
      toast({
        title: "Cerrando sesión",
        description: "Saliendo de la sesión...",
        duration: 2000,
      });
      
      // Pequeño retraso para que la notificación se muestre antes de cerrar sesión
      setTimeout(() => {
        logout();
      }, 500);
    } catch (error) {
      console.error("Error al cerrar sesión:", error);
      toast({
        title: "Error",
        description: "Hubo un problema al cerrar sesión, inténtalo de nuevo.",
        variant: "destructive",
      });
    }
  };

  // Manejar la selección de un pedido
  const handleSelectOrder = useCallback((order: Order) => {
    setSelectedOrder(order);
    setIsModalOpen(true);
  }, []);

  // Manejar la actualización de estado de un pedido
  const handleStatusUpdate = useCallback(async (orderId: string, newStatus: string) => {
    try {
      // Marcar como actualizando
      setUpdatingOrderIds(prev => {
        const newSet = new Set(prev);
        newSet.add(orderId);
        return newSet;
      });

      await updateOrderStatus(orderId, newStatus);

      // Mostrar notificación de éxito
      toast({
        title: "Estado actualizado",
        description: `El pedido ha sido marcado como "${newStatus.charAt(0).toUpperCase() + newStatus.slice(1)}"`,
        variant: "default",
      });
    } catch (err) {
      toast({
        variant: "destructive",
        title: "Error",
        description: err instanceof Error ? err.message : "No se pudo actualizar el estado.",
      });
    } finally {
      // Quitar de la lista de actualizando
      setUpdatingOrderIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(orderId);
        return newSet;
      });
    }
  }, [updateOrderStatus, toast]);

  // Manejar la eliminación de un pedido
  const handleDeleteOrder = useCallback((orderId: string) => {
    setPendingDeleteOrderId(orderId);
    setIsConfirmDialogOpen(true);
  }, []);

  // Confirmar eliminación de pedido
  const confirmDeleteOrder = useCallback(async () => {
    if (!pendingDeleteOrderId) return;

    try {
      await deleteOrder(pendingDeleteOrderId);
      toast({
        title: "Pedido eliminado",
        description: "El pedido ha sido eliminado exitosamente",
        variant: "default",
      });

      // Si el pedido eliminado es el que está seleccionado, cerrar el modal
      if (selectedOrder?.id === pendingDeleteOrderId) {
        setIsModalOpen(false);
        setSelectedOrder(null);
      }
    } catch (err) {
      toast({
        variant: "destructive",
        title: "Error",
        description: err instanceof Error ? err.message : "No se pudo eliminar el pedido.",
      });
    } finally {
      setIsConfirmDialogOpen(false);
      setPendingDeleteOrderId(null);
    }
  }, [pendingDeleteOrderId, deleteOrder, toast, selectedOrder]);

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-10 border-b bg-background shadow-sm">
        <div className="container flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <Emoji symbol="🍟" label="papas fritas" className="text-2xl" />
            <h1 className="text-lg font-semibold md:text-xl">Go Papa Dashboard</h1>
          </div>
          <div className="flex items-center gap-4">
            {/* Botón de actualización */}
            <Button 
              variant="outline" 
              onClick={() => refreshOrders()}
              className="hidden md:flex"
            >
              Actualizar
            </Button>
            
            {/* Selector de tema */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="icon" className="rounded-full h-9 w-9">
                  {theme === "dark" ? <MoonIcon className="h-4 w-4" /> : <SunIcon className="h-4 w-4" />}
                  <span className="sr-only">Cambiar tema</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setTheme("light")}>
                  Claro
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTheme("dark")}>
                  Oscuro
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTheme("system")}>
                  Sistema
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            
            {/* Menú de usuario */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button 
                  variant="ghost" 
                  className="relative h-9 rounded-full border border-muted flex items-center gap-2 pr-2"
                >
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      {getUserInitials()}
                    </AvatarFallback>
                  </Avatar>
                  <span className="hidden md:inline-block font-medium truncate max-w-[120px]">
                    {authState.user?.name || "Usuario"}
                  </span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-60">
                <DropdownMenuLabel>Mi cuenta</DropdownMenuLabel>
                <div className="px-2 py-1.5">
                  <p className="text-sm font-medium truncate">{authState.user?.name || "Usuario"}</p>
                  <p className="text-xs text-muted-foreground truncate">{authState.user?.email || ""}</p>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  className="text-red-500 focus:text-red-500 cursor-pointer"
                  onClick={handleLogout}
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Cerrar sesión
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>
      <main className="flex-1 overflow-auto p-4">
        <div className="container mx-auto space-y-6">
          {/* Estadísticas */}
          <Statistics stats={stats} isLoading={isLoading} />

          {/* Lista de Órdenes */}
          <OrdersList
            orders={orders}
            onSelectOrder={handleSelectOrder}
            onStatusUpdate={handleStatusUpdate}
            onDeleteOrder={handleDeleteOrder}
            updatingOrderIds={updatingOrderIds}
            setUpdatingOrderIds={setUpdatingOrderIds}
            isLoading={isLoading}
            error={error}
          />

          {/* Modal de Orden */}
          {selectedOrder && (
            <OrderModal
              order={selectedOrder}
              open={isModalOpen}
              onOpenChange={setIsModalOpen}
              onStatusUpdate={handleStatusUpdate}
              onDeleteOrder={handleDeleteOrder}
              isUpdating={updatingOrderIds.has(selectedOrder.id)}
            />
          )}

          {/* Diálogo de Confirmación */}
          <ConfirmDialog
            open={isConfirmDialogOpen}
            onOpenChange={setIsConfirmDialogOpen}
            onConfirm={confirmDeleteOrder}
            title="Eliminar Pedido"
            description="¿Estás seguro que deseas eliminar este pedido? Esta acción no se puede deshacer."
          />
        </div>
      </main>
    </div>
  );
} 