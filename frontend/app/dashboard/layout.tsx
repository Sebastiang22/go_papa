"use client";

import ProtectedRoute from "@/components/auth/protected-route";
import { ReactNode } from "react";

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <ProtectedRoute>
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
    </ProtectedRoute>
  );
} 