import type { Metadata } from "next"
import { DashboardClient } from "@/components/features/dashboard"

export const metadata: Metadata = {
  title: "Dashboard - Go Papa",
  description: "Panel de control para la gestión de pedidos de Go Papa",
}

/**
 * Página principal del dashboard
 * Usamos un componente del lado del servidor que luego carga el dashboard del cliente
 */
export default function DashboardPage() {
  return (
    <main className="flex-1 overflow-hidden">
      <DashboardClient />
    </main>
  )
}

