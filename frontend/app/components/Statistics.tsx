import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function Statistics() {
  // Mock data - replace with actual statistics
  const stats = {
    totalOrders: 25,
    pendingOrders: 10,
    completedOrders: 15,
    totalRevenue: 350.5,
  }

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Today's Statistics</CardTitle>
      </CardHeader>
      <CardContent>
        <p>
          <strong>Total Orders:</strong> {stats.totalOrders}
        </p>
        <p>
          <strong>Pending Orders:</strong> {stats.pendingOrders}
        </p>
        <p>
          <strong>Completed Orders:</strong> {stats.completedOrders}
        </p>
        <p>
          <strong>Total Revenue:</strong> ${stats.totalRevenue.toFixed(2)}
        </p>
      </CardContent>
    </Card>
  )
}

