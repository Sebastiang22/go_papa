"use client"

import { useState, useEffect, useCallback } from "react"
import { MoonIcon, SunIcon } from "lucide-react"
import { useTheme } from "next-themes"
import { useToast } from "@/components/ui/use-toast"

import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { OrderList } from "@/components/order-list"
import { OrderModal } from "@/components/order-modal"
import { Statistics } from "@/components/statistics"
import type { Order } from "./order-list"
import { ConfirmDialog } from "@/components/confirm-dialog"

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

interface BackendData {
  stats: {
    total_orders: number
    pending_orders: number
    complete_orders: number
    total_sales: number
  }
  orders: Order[]
}

export default function Dashboard() {
  const { theme, setTheme } = useTheme()
  const { toast } = useToast()
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [backendData, setBackendData] = useState<BackendData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [updatingOrderIds, setUpdatingOrderIds] = useState<Set<string>>(new Set())
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false)
  const [pendingDeleteOrderId, setPendingDeleteOrderId] = useState<string | null>(null)

  const API_URL = "http://127.0.0.1:8000";

  // Función para cargar los datos con useCallback para evitar recreaciones innecesarias
  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      const response = await fetch(`${API_URL}/orders/today`, { method: "GET" });
      
      if (response.status === 404) {
        // Caso especial: No hay pedidos para hoy
        setBackendData({
          stats: {
            total_orders: 0,
            pending_orders: 0,
            complete_orders: 0,
            total_sales: 0
          },
          orders: []
        })
        return
      }
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`)
      }
      
      const data: BackendData = await response.json()
      console.log("Datos recibidos del backend:", data)
      setBackendData(data)
      
      // También actualizamos el pedido seleccionado si existe
      if (selectedOrder) {
        const updatedOrder = data.orders.find(order => order.id === selectedOrder.id);
        if (updatedOrder) {
          setSelectedOrder(updatedOrder);
        }
      }
    } catch (err) {
      console.error("Error fetching data:", err)
      setError("Error al cargar los datos. Por favor, intente nuevamente.")
      toast({
        variant: "destructive",
        title: "Error",
        description: "No se pudieron cargar los pedidos. Por favor, intente nuevamente.",
      })
    } finally {
      setIsLoading(false)
    }
  }, [API_URL, toast, selectedOrder])

  // Cargar datos iniciales y configurar actualización periódica
  useEffect(() => {
    fetchData()
    
    // Configurar intervalo para actualización automática cada 30 segundos
    const intervalId = setInterval(fetchData, 30000)
    
    // Limpieza al desmontar
    return () => clearInterval(intervalId)
  }, [fetchData])

  const handleSelectOrder = (order: Order) => {
    setSelectedOrder(order)
    setIsModalOpen(true)
  }

  const handleStatusUpdate = async (orderId: string, newStatus: string) => {
    try {
      // Marcar como actualizando
      setUpdatingOrderIds(prev => {
        const newSet = new Set(prev)
        newSet.add(orderId)
        return newSet
      })
      
      console.log(`Actualizando pedido ${orderId} a estado: ${newStatus}`)
      
      // Actualización optimista de la UI
      if (backendData) {
        const updatedOrders = backendData.orders.map(order => 
          order.id === orderId ? { ...order, state: newStatus } : order
        );
        
        setBackendData(prev => prev ? {
          ...prev,
          orders: updatedOrders
        } : null);
        
        // Actualizar el pedido seleccionado si es el que estamos modificando
        if (selectedOrder && selectedOrder.id === orderId) {
          setSelectedOrder({ ...selectedOrder, state: newStatus });
        }
      }
      
      // Llamada a la API para actualizar el estado
      const response = await fetch(`${API_URL}/orders/update_state`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          order_id: orderId,
          state: newStatus
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `Error: ${response.status}`)
      }
      
      const updatedOrder = await response.json()
      console.log("Respuesta del servidor:", updatedOrder)
      
      // Mostrar notificación de éxito
      toast({
        title: "Estado actualizado",
        description: `El pedido ha sido marcado como "${newStatus.charAt(0).toUpperCase() + newStatus.slice(1)}"`,
        variant: "default",
      })
      
      // Recargar los datos para asegurarnos de tener información actualizada
      await fetchData()
      
    } catch (err) {
      console.error("Error updating order status:", err)
      toast({
        variant: "destructive",
        title: "Error",
        description: err instanceof Error ? err.message : "No se pudo actualizar el estado del pedido.",
      })
      
      // Recargar datos en caso de error para revertir cambios optimistas incorrectos
      await fetchData()
    } finally {
      // Quitar la marca de actualización
      setUpdatingOrderIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(orderId)
        return newSet
      })
    }
  }

  // Actualizar la función handleDeleteOrder
  const handleDeleteOrder = async (orderId: string) => {
    // En lugar de mostrar confirm() directamente, guardamos el ID y mostramos el diálogo
    setPendingDeleteOrderId(orderId)
    setIsConfirmDialogOpen(true)
  }

  // Añadir una nueva función para manejar la eliminación confirmada
  const handleConfirmedDelete = async () => {
    // Verificar que tenemos un ID válido
    if (!pendingDeleteOrderId) return

    const orderIdToDelete = pendingDeleteOrderId
    
    try {
      // Marcar como actualizando
      setUpdatingOrderIds(prev => {
        const newSet = new Set(prev)
        newSet.add(orderIdToDelete)
        return newSet
      })
      
      console.log(`Eliminando pedido ${orderIdToDelete}`)
      
      // Llamada a la API para eliminar el pedido
      const response = await fetch(`${API_URL}/orders/${orderIdToDelete}`, {
        method: "DELETE",
      })
      
      if (!response.ok) {
        throw new Error(`Error al eliminar pedido: ${response.status}`)
      }
      
      // Actualización optimista de la UI (eliminar de la lista)
      if (backendData) {
        const updatedOrders = backendData.orders.filter(order => order.id !== orderIdToDelete)
        
        setBackendData(prev => prev ? {
          ...prev,
          orders: updatedOrders,
          stats: {
            ...prev.stats,
            total_orders: prev.stats.total_orders - 1,
            pending_orders: prev.stats.pending_orders - (
              selectedOrder?.state === 'pendiente' ? 1 : 0
            ),
            complete_orders: prev.stats.complete_orders - (
              selectedOrder?.state === 'completado' ? 1 : 0
            )
          }
        } : null)
        
        // Si el pedido eliminado era el seleccionado, cerrar el modal
        if (selectedOrder && selectedOrder.id === orderIdToDelete) {
          setSelectedOrder(null)
          setIsModalOpen(false)
        }
      }
      
      toast({
        title: "Pedido eliminado",
        description: `El pedido #${orderIdToDelete} ha sido eliminado correctamente.`,
      })
      
      // Recargar los datos para asegurarnos de tener información actualizada
      await fetchData()
    } catch (err) {
      console.error("Error al eliminar pedido:", err)
      toast({
        variant: "destructive",
        title: "Error",
        description: err instanceof Error ? err.message : "No se pudo eliminar el pedido.",
      })
      
      // Recargar datos en caso de error
      await fetchData()
    } finally {
      // Quitar la marca de actualización
      setUpdatingOrderIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(orderIdToDelete)
        return newSet
      })
      
      // Limpiar el ID pendiente
      setPendingDeleteOrderId(null)
    }
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Error</h2>
          <p className="text-muted-foreground mb-4">{error}</p>
          <Button onClick={() => window.location.reload()} className="bg-[#B22222] hover:bg-[#8B0000] text-white">Intentar nuevamente</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="border-b bg-[#B22222] text-white">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center space-x-4">
              <Emoji symbol="🍟" label="papas fritas" className="text-4xl" />
              <div>
                <h1 className="text-2xl font-bold tracking-tight">¡GO PAPA!</h1>
                <p className="text-sm text-white/80">Gestiona los pedidos de tu Food Truck</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon" className="border-white/20 bg-transparent text-white hover:bg-white/10 hover:text-white">
                    <SunIcon className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
                    <MoonIcon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
                    <span className="sr-only">Cambiar tema</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setTheme("light")}>Claro</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setTheme("dark")}>Oscuro</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setTheme("system")}>Sistema</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </header>
      <main className="flex-1 container mx-auto px-4 py-6">
        <div className="mb-6">{backendData && <Statistics stats={backendData.stats} />}</div>
        <div>
          {isLoading && !backendData ? (
            <div className="text-center py-12">
              <Emoji symbol="⏳" label="cargando" className="text-4xl block mx-auto mb-4" />
              <p>Cargando pedidos...</p>
            </div>
          ) : backendData && backendData.orders.length > 0 ? (
            <OrderList
              orders={backendData.orders}
              onSelectOrder={handleSelectOrder}
              onStatusUpdate={handleStatusUpdate}
              onDeleteOrder={handleDeleteOrder}
              updatingOrderIds={updatingOrderIds}
            />
          ) : (
            <div className="text-center py-12 border rounded-lg bg-card">
              <Emoji symbol="🍟" label="papas fritas" className="text-6xl block mx-auto mb-4" />
              <h3 className="text-xl font-medium mb-2">No hay pedidos para hoy</h3>
              <p className="text-muted-foreground">
                Cuando lleguen nuevos pedidos, aparecerán aquí.
              </p>
              <div className="mt-4 text-sm text-[#B22222]">¡GO PAPA! Food Truck</div>
            </div>
          )}
        </div>

        <OrderModal
          order={selectedOrder}
          open={isModalOpen}
          onOpenChange={setIsModalOpen}
          onStatusUpdate={handleStatusUpdate}
          onDeleteOrder={handleDeleteOrder}
          isUpdating={selectedOrder ? updatingOrderIds.has(selectedOrder.id) : false}
        />

        <ConfirmDialog
          title="Confirmar eliminación"
          description="¿Estás seguro de que deseas eliminar este pedido? Esta acción no se puede deshacer."
          open={isConfirmDialogOpen}
          onOpenChange={setIsConfirmDialogOpen}
          onConfirm={handleConfirmedDelete}
          confirmText="Eliminar"
          cancelText="Cancelar"
          isDestructive={true}
        />
      </main>
    </div>
  )
}

