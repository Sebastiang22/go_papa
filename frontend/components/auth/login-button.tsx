"use client";

import { Button, ButtonProps } from "@/components/ui/button";
import { useAuth } from "@/lib/providers/auth-provider";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

interface LoginButtonProps extends ButtonProps {
  label?: string;
}

/**
 * Botón para iniciar sesión con Microsoft Entra ID.
 */
export function LoginButton({ 
  label = "Iniciar sesión con Microsoft", 
  className, 
  ...props 
}: LoginButtonProps) {
  const { authState, login } = useAuth();
  
  return (
    <Button
      onClick={login}
      disabled={authState.isLoading}
      className={cn("relative", className)}
      {...props}
    >
      {authState.isLoading ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Conectando...
        </>
      ) : (
        <>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 23 23"
            className="mr-2"
          >
            <path fill="#f3f3f3" d="M0 0h23v23H0z"></path>
            <path fill="#f35325" d="M1 1h10v10H1z"></path>
            <path fill="#81bc06" d="M12 1h10v10H12z"></path>
            <path fill="#05a6f0" d="M1 12h10v10H1z"></path>
            <path fill="#ffba08" d="M12 12h10v10H12z"></path>
          </svg>
          {label}
        </>
      )}
    </Button>
  );
} 