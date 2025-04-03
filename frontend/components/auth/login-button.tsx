"use client";

import { Button, ButtonProps } from "@/components/ui/button";
import { useAuth } from "@/lib/providers/auth-provider";

interface LoginButtonProps extends ButtonProps {
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
}

export function LoginButton({ 
  children, 
  variant = "default", 
  size = "default", 
  className,
  ...props 
}: LoginButtonProps) {
  const { login } = useAuth();
  
  return (
    <Button
      variant={variant}
      size={size}
      className={className}
      onClick={login}
      {...props}
    >
      {children || "Iniciar Sesión con Microsoft"}
    </Button>
  );
} 