import { NextRequest, NextResponse } from "next/server";

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const orderId = params.id;
    
    // Conectar con el backend real
    const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";
    
    const response = await fetch(`${BACKEND_URL}/orders/${orderId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || "Error al eliminar el pedido" },
        { status: response.status }
      );
    }
    
    return NextResponse.json(
      { message: `Pedido ${orderId} eliminado correctamente` },
      { status: 200 }
    );
  } catch (error) {
    console.error("Error al eliminar pedido:", error);
    return NextResponse.json(
      { error: "Error al procesar la solicitud" },
      { status: 500 }
    );
  }
} 