"use client";

import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface SpinnerProps {
  /**
   * Tamaño del spinner: small (sm), medium (md), large (lg)
   */
  size?: "sm" | "md" | "lg";
  
  /**
   * Clase CSS adicional
   */
  className?: string;
}

/**
 * Componente Spinner para indicar estados de carga.
 */
export function Spinner({ size = "md", className }: SpinnerProps) {
  // Mapear tamaño a clases de dimensión
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-8 w-8",
    lg: "h-12 w-12",
  };
  
  return (
    <Loader2 
      className={cn(
        "animate-spin text-primary", 
        sizeClasses[size],
        className
      )} 
    />
  );
} 