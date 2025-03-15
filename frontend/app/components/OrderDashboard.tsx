"use client"

import { useState } from "react"
import OrderList from "./OrderList"
import OrderDetail from "./OrderDetail"
import SearchBar from "./SearchBar"
import Statistics from "./Statistics"

export default function OrderDashboard() {
  const [selectedOrder, setSelectedOrder] = useState(null)
  const [searchTerm, setSearchTerm] = useState("")

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Café Order Management</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          <SearchBar onSearch={setSearchTerm} />
          <OrderList searchTerm={searchTerm} onSelectOrder={setSelectedOrder} />
        </div>
        <div>
          <Statistics />
          {selectedOrder && <OrderDetail order={selectedOrder} />}
        </div>
      </div>
    </div>
  )
}

