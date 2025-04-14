import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

// Nueva URL base para el backend
const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://af-gopapa.azurewebsites.net';

export async function GET(request: NextRequest) {
  // Add CORS headers
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  }

  try {
    // Redirigir la solicitud al nuevo backend
    const response = await fetch(`${API_URL}/orders/today`, {
      headers: {
        "Content-Type": "application/json",
      },
    });
    
    const data = await response.json();
    return NextResponse.json(data, { headers })
  } catch (error) {
    console.error("Error al obtener órdenes:", error)
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

