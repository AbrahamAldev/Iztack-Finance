"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

/**
 * AuthGuard - Client component that protects app routes.
 * Redirects to /login if no JWT token is present in localStorage.
 */
export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("iztack_token");
    if (!token) {
      router.replace("/login");
    } else {
      setIsAuthenticated(true);
    }
  }, [router]);

  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="text-4xl animate-pulse mb-4">🏦</div>
          <p className="text-gray-500">Cargando...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}