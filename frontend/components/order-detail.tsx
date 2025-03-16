import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Order } from "./order-list"

const statusMap = {
  pending: "Pendiente",
  "in-progress": "En Preparación",
  completed: "Completado",
}

interface OrderDetailProps {
  order: Order
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

export function OrderDetail({ order, onStatusUpdate }: OrderDetailProps) {
  const statusColors = {
    pendiente: "bg-yellow-500",
    "en preparación": "bg-blue-500",
    completado: "bg-green-500",
  }

  // Calcular el total del pedido
  const orderTotal = order.products.reduce((total, product) => {
    return total + product.price * product.quantity
  }, 0)

  return (
    <Card className="sticky top-6">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Pedido #{order.id}</span>
          <Badge className={statusColors[order.state] || "bg-gray-500"}>
            {order.state.charAt(0).toUpperCase() + order.state.slice(1)}
          </Badge>
        </CardTitle>
        <CardDescription>Detalles y acciones del pedido</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Cliente</label>
            <p className="mt-1">{order.customer_name}</p>
          </div>
          <div>
            <label className="text-sm font-medium">Dirección</label>
            <p className="mt-1">{order.table_id}</p>
          </div>
          <div>
            <label className="text-sm font-medium">Productos</label>
            <div className="mt-2 space-y-2">
              {order.products.map((product, index) => (
                <div key={index} className="flex justify-between items-center text-sm">
                  <div>
                    <span className="font-medium">{product.name}</span>
                    <span className="text-muted-foreground ml-2">
                      ({formatCOP(product.price)} x {product.quantity})
                    </span>
                  </div>
                  <span className="font-medium">{formatCOP(product.price * product.quantity)}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <label className="text-sm font-medium">Total</label>
            <p className="mt-1 font-bold text-lg">{formatCOP(orderTotal)}</p>
          </div>
          <div>
            <label className="text-sm font-medium">Fecha de creación</label>
            <p className="mt-1">{formatDate(order.created_at)}</p>
          </div>
          <div>
            <label className="text-sm font-medium">Última actualización</label>
            <p className="mt-1">{formatDate(order.updated_at)}</p>
          </div>
          <div>
            <label className="text-sm font-medium">Estado</label>
            <Select defaultValue={order.state} onValueChange={(value: string) => onStatusUpdate(order.id, value)}>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Seleccionar estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pendiente">Pendiente</SelectItem>
                <SelectItem value="en preparación">En Preparación</SelectItem>
                <SelectItem value="completado">Completado</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex flex-col gap-2">
        <Button className="w-full" variant="default" onClick={() => onStatusUpdate(order.id, "completado")}>
          Marcar como Completado
        </Button>
        <Button className="w-full" variant="destructive" onClick={() => onStatusUpdate(order.id, "cancelado")}>
          Cancelar Pedido
        </Button>
      </CardFooter>
    </Card>
  )
}

