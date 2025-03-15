import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

// Mock data - replace with actual data fetching logic
const orders = [
  { id: 1, customer: "Alice", items: ["Cappuccino", "Croissant"], total: 8.5, status: "Pending" },
  { id: 2, customer: "Bob", items: ["Latte", "Sandwich"], total: 12.0, status: "In Progress" },
  { id: 3, customer: "Charlie", items: ["Espresso", "Muffin"], total: 6.5, status: "Completed" },
]

export default function OrderList({ searchTerm, onSelectOrder }) {
  const filteredOrders = orders.filter(
    (order) =>
      order.customer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.items.some((item) => item.toLowerCase().includes(searchTerm.toLowerCase())),
  )

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Order ID</TableHead>
          <TableHead>Customer</TableHead>
          <TableHead>Items</TableHead>
          <TableHead>Total</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {filteredOrders.map((order) => (
          <TableRow key={order.id} onClick={() => onSelectOrder(order)} className="cursor-pointer hover:bg-gray-100">
            <TableCell>{order.id}</TableCell>
            <TableCell>{order.customer}</TableCell>
            <TableCell>{order.items.join(", ")}</TableCell>
            <TableCell>${order.total.toFixed(2)}</TableCell>
            <TableCell>{order.status}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

