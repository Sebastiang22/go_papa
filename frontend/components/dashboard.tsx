"use client"

import { useState, useEffect } from "react"
import { MoonIcon, SunIcon, Coffee } from "lucide-react"
import { useTheme } from "next-themes"
import { useToast } from "@/components/ui/use-toast"

import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { OrderList } from "@/components/order-list"
import { OrderModal } from "@/components/order-modal"
import { Statistics } from "@/components/statistics"
import type { Order } from "./order-list"

interface BackendData {
  stats: {
    total_orders: number
    pending_orders: number
    complete_orders: number
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

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        setError(null)
  
        // Llamada real a tu API
        const response = await fetch("https://webappagentsgraphs-tars-beb0ara7htgmdndn.eastus2-01.azurewebsites.net/api/agent/chat/orders")
        if (!response.ok) {
          throw new Error(`Error: ${response.status}`)
        }
        const data: BackendData = await response.json()
  
        setBackendData(data)
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
    }
  
    fetchData()
  }, [toast])
  

  const handleSelectOrder = (order: Order) => {
    setSelectedOrder(order)
    setIsModalOpen(true)
  }

  const handleStatusUpdate = async (orderId: string, newStatus: string) => {
    try {
      // Aquí normalmente harías una llamada a la API para actualizar el estado
      // Por ahora, solo actualizamos el estado local
      if (backendData) {
        const updatedOrders = backendData.orders.map((order) =>
          order.id === orderId ? { ...order, state: newStatus, updated_at: new Date().toISOString() } : order,
        )

        // Actualizar estadísticas
        const stats = { ...backendData.stats }
        const oldOrder = backendData.orders.find((o) => o.id === orderId)
        const newOrder = updatedOrders.find((o) => o.id === orderId)

        if (oldOrder && newOrder && oldOrder.state !== newOrder.state) {
          // Decrementar contador del estado anterior
          if (oldOrder.state === "pendiente") stats.pending_orders--
          else if (oldOrder.state === "completado") stats.complete_orders--

          // Incrementar contador del nuevo estado
          if (newOrder.state === "pendiente") stats.pending_orders++
          else if (newOrder.state === "completado") stats.complete_orders++
        }

        setBackendData({ ...backendData, orders: updatedOrders, stats })

        if (selectedOrder && selectedOrder.id === orderId) {
          setSelectedOrder({ ...selectedOrder, state: newStatus, updated_at: new Date().toISOString() })
        }

        toast({
          title: "Estado actualizado",
          description: "El estado del pedido ha sido actualizado exitosamente.",
        })
      }
    } catch (err) {
      console.error("Error updating order status:", err)
      toast({
        variant: "destructive",
        title: "Error",
        description: "No se pudo actualizar el estado del pedido. Por favor, intente nuevamente.",
      })
    }
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Error</h2>
          <p className="text-muted-foreground mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>Intentar nuevamente</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="border-b bg-background">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center space-x-4">
              <Coffee className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold tracking-tight">Panel del Barista</h1>
                <p className="text-sm text-muted-foreground">Gestiona los pedidos de tu café</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon">
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
          {backendData && (
            <OrderList
              orders={backendData.orders}
              onSelectOrder={handleSelectOrder}
              onStatusUpdate={handleStatusUpdate}
            />
          )}
        </div>

        <OrderModal
          order={selectedOrder}
          open={isModalOpen}
          onOpenChange={setIsModalOpen}
          onStatusUpdate={handleStatusUpdate}
        />
      </main>
    </div>
  )
}

