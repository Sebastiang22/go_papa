import { Badge } from "@/components/ui/badge"

interface StatusBadgeProps {
  status: string
}

export function StatusBadge({ status }: StatusBadgeProps) {
  switch (status.toLowerCase()) {
    case "pendiente":
      return (
        <Badge variant="outline" className="bg-amber-100 text-amber-800 border-amber-200">
          Pendiente
        </Badge>
      )
    case "en preparación":
      return (
        <Badge variant="outline" className="bg-blue-100 text-blue-800 border-blue-200">
          En preparación
        </Badge>
      )
    case "completado":
      return (
        <Badge variant="outline" className="bg-green-100 text-green-800 border-green-200">
          Completado
        </Badge>
      )
    default:
      return (
        <Badge variant="outline" className="bg-muted text-muted-foreground">
          {status}
        </Badge>
      )
  }
} 