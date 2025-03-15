import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export async function GET(request: NextRequest) {
  // Add CORS headers
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  }

  try {
    // Aquí normalmente harías tu llamada a la base de datos o servicio
    const mockData = {
      stats: {
        total_orders: 6,
        pending_orders: 6,
        complete_orders: 6,
      },
      orders: [
        {
          table_id: "2",
          product_name: "hamburguesa",
          cantidad: 1,
          created_at: "2025-02-14T20:07:50.398659",
          updated_at: "2025-02-14T20:07:50.398659",
          state: "pendiente",
          id: "2025-02-14T20:07:50.398659-2",
        },
      ],
    }

    return NextResponse.json(mockData, { headers })
  } catch (error) {
    console.error("Error fetching orders:", error)
    return NextResponse.json({ error: "Error interno del servidor" }, { status: 500, headers })
  }
}

export async function OPTIONS(request: NextRequest) {
  return NextResponse.json(
    {},
    {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
      },
    },
  )
}

