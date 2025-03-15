import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function OrderDetail({ order }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Order #{order.id}</CardTitle>
      </CardHeader>
      <CardContent>
        <p>
          <strong>Customer:</strong> {order.customer}
        </p>
        <p>
          <strong>Items:</strong>
        </p>
        <ul>
          {order.items.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
        <p>
          <strong>Total:</strong> ${order.total.toFixed(2)}
        </p>
        <p>
          <strong>Status:</strong> {order.status}
        </p>
        <div className="mt-4">
          <Button className="mr-2">Update Status</Button>
          <Button variant="outline">Cancel Order</Button>
        </div>
      </CardContent>
    </Card>
  )
}

