"use client"

import { useState, useEffect } from "react"
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
import { Clock, User, CalendarDays, RefreshCw, AlertCircle, Loader2, Trash2, MapPin } from "lucide-react"
import { 
  Order, 
  OrderState, 
  OrderStatusCallback, 
  OrderDeleteCallback 
} from "@/lib/types"
import { formatCOP, formatDateLong } from "@/lib/utils/format"

interface OrderModalProps {
  order: Order | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onStatusUpdate: OrderStatusCallback
  onDeleteOrder: OrderDeleteCallback
  isUpdating?: boolean
}

/**
 * Modal para mostrar detalles y gestionar un pedido
 */
export function OrderModal({ 
  order, 
  open, 
  onOpenChange, 
  onStatusUpdate, 
  onDeleteOrder, 
  isUpdating = false 
}: OrderModalProps) {
  if (!order) return null

  // Estado local para controlar el estado actual del pedido
  const [currentState, setCurrentState] = useState<string>(order.state)

  // Sincronizar el estado local cuando cambia el pedido
  useEffect(() => {
    if (order) {
      setCurrentState(order.state)
    }
  }, [order])

  const statusColors = {
    [OrderState.PENDING]: "bg-yellow-500",
    [OrderState.PREPARING]: "bg-blue-500",
    [OrderState.COMPLETED]: "bg-green-500",
  }
  
  const handleStatusChange = async (value: string) => {
    try {
      // Actualizar el estado local inmediatamente
      setCurrentState(value)
      // Luego actualizar en el backend
      await onStatusUpdate(order.id, value)
    } catch (err) {
      // Si hay error, revertir al estado anterior
      setCurrentState(order.state)
      console.error("Error al actualizar estado:", err)
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
            <Badge className={`${statusColors[currentState as OrderState] || "bg-gray-500"} whitespace-nowrap`}>
              {currentState.charAt(0).toUpperCase() + currentState.slice(1)}
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
                <MapPin className="h-4 w-4" />
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
              <div className="font-medium text-sm">{formatDateLong(order.created_at)}</div>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <RefreshCw className="h-4 w-4" />
                <span>Última actualización</span>
              </div>
              <div className="font-medium text-sm">{formatDateLong(order.updated_at)}</div>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              <span>Estado del pedido</span>
            </div>
            <Select 
              value={currentState}
              onValueChange={handleStatusChange}
              disabled={isUpdating}
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar estado">
                  {isUpdating && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                  {currentState.charAt(0).toUpperCase() + currentState.slice(1)}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={OrderState.PENDING}>Pendiente</SelectItem>
                <SelectItem value={OrderState.PREPARING}>En Preparación</SelectItem>
                <SelectItem value={OrderState.COMPLETED}>Completado</SelectItem>
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
            variant="destructive"
            className="w-full"
            onClick={() => {
              onDeleteOrder(order.id);
              onOpenChange(false);
            }}
            disabled={isUpdating}
          >
            {isUpdating ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4 mr-2" />
            )}
            Eliminar Pedido
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
} 