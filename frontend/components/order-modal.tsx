"use client"

import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Clock, User, CalendarDays, RefreshCw, AlertCircle, Loader2 } from "lucide-react"
import type { Order } from "./order-list"

interface OrderModalProps {
  order: Order | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onStatusUpdate: (orderId: string, newStatus: string) => void
}

// Función para formatear números a pesos colombianos
const formatCOP = (value: number) => {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString("es-CO", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export function OrderModal({ order, open, onOpenChange, onStatusUpdate }: OrderModalProps) {
  const [isUpdating, setIsUpdating] = useState(false)
  
  if (!order) return null

  const statusColors = {
    pendiente: "bg-yellow-500",
    "en preparación": "bg-blue-500",
    completado: "bg-green-500",
  }
  
  const handleStatusChange = async (value: string) => {
    setIsUpdating(true)
    try {
      await onStatusUpdate(order.id, value)
      // No necesitamos hacer nada más aquí, ya que el componente Dashboard
      // se encargará de recargar los datos y actualizar el estado
    } finally {
      setIsUpdating(false)
    }
  }

  // Calcular el total del pedido
  const orderTotal = order.products.reduce((total, product) => {
    return total + product.price * product.quantity
  }, 0)

  return (
    <Dialog open={open} onOpenChange={(newOpen) => !isUpdating && onOpenChange(newOpen)}>
      <DialogContent className="w-[95%] max-w-[550px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <DialogTitle className="text-xl">Pedido #{order.id}</DialogTitle>
            <Badge className={`${statusColors[order.state] || "bg-gray-500"} whitespace-nowrap`}>
              {order.state.charAt(0).toUpperCase() + order.state.slice(1)}
            </Badge>
          </div>
          <DialogDescription>Detalles y gestión del pedido</DialogDescription>
        </DialogHeader>

        <div className="grid gap-6 py-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <User className="h-4 w-4" />
                <span>Cliente</span>
              </div>
              <div className="font-medium">{order.customer_name}</div>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span>Dirección</span>
              </div>
              <div className="font-medium">{order.table_id}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <CalendarDays className="h-4 w-4" />
                <span>Fecha de creación</span>
              </div>
              <div className="font-medium text-sm">{formatDate(order.created_at)}</div>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <RefreshCw className="h-4 w-4" />
                <span>Última actualización</span>
              </div>
              <div className="font-medium text-sm">{formatDate(order.updated_at)}</div>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              <span>Estado del pedido</span>
            </div>
            <Select 
              defaultValue={order.state} 
              onValueChange={handleStatusChange}
              disabled={isUpdating}
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar estado">
                  {isUpdating && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                  {order.state.charAt(0).toUpperCase() + order.state.slice(1)}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pendiente">Pendiente</SelectItem>
                <SelectItem value="en preparación">En Preparación</SelectItem>
                <SelectItem value="completado">Completado</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Separator />

          <div>
            <h3 className="font-medium mb-3">Productos</h3>
            <Card>
              <CardContent className="p-0">
                <div className="divide-y">
                  {order.products.map((product, index) => (
                    <div key={index} className="p-4">
                      <div className="flex justify-between items-start mb-1">
                        <div>
                          <div className="font-medium">{product.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {formatCOP(product.price)} x {product.quantity}
                          </div>
                        </div>
                        <div className="font-medium">{formatCOP(product.price * product.quantity)}</div>
                      </div>

                      {product.observations && (
                        <div className="mt-2 p-2 bg-muted rounded-md text-sm flex items-start gap-2">
                          <AlertCircle className="h-4 w-4 text-amber-500 mt-0.5 flex-shrink-0" />
                          <span>{product.observations}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="bg-muted/50 p-4 rounded-lg">
            <div className="flex items-center justify-between font-bold">
              <span className="text-base">Total</span>
              <span className="text-lg">{formatCOP(orderTotal)}</span>
            </div>
          </div>
        </div>

        <DialogFooter className="flex flex-col sm:flex-row gap-2">
          <Button 
            variant="outline" 
            className="w-full" 
            onClick={() => onOpenChange(false)}
            disabled={isUpdating}
          >
            Cerrar
          </Button>
          <Button
            className="w-full"
            onClick={() => {
              setIsUpdating(true)
              onStatusUpdate(order.id, "completado")
                .finally(() => {
                  setIsUpdating(false)
                  onOpenChange(false)
                })
            }}
            disabled={isUpdating || order.state === "completado"}
          >
            {isUpdating ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Actualizando...
              </>
            ) : (
              "Marcar como Completado"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

