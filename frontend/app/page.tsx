import type { Metadata } from "next"
import Dashboard from "@/components/dashboard"

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Order management dashboard for café staff",
}

export default function DashboardPage() {
  return <Dashboard />
}

