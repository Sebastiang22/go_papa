import { cn } from "@/lib/utils";

interface SpinnerProps {
  size?: "sm" | "default" | "lg" | "xl";
  className?: string;
}

export function Spinner({ size = "default", className }: SpinnerProps) {
  const sizeClasses = {
    sm: "h-4 w-4",
    default: "h-6 w-6",
    lg: "h-8 w-8",
    xl: "h-12 w-12",
  };
  
  return (
    <div
      className={cn(
        "animate-spin rounded-full border-2 border-current border-t-transparent",
        sizeClasses[size],
        className
      )}
    >
      <span className="sr-only">Cargando...</span>
    </div>
  );
} 