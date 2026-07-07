"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

/**
 * Layout for authenticated app routes (/app/*).
 * Redirects to /login if not authenticated.
 */
export default function AppLayout({ children }: { children: React.ReactNode }) {
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

  function handleLogout() {
    localStorage.removeItem("iztack_token");
    router.push("/login");
  }

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

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/app/dashboard" className="text-xl font-bold text-sky-600">
            🏦 Iztack-Finance
          </Link>
          <div className="flex gap-4 items-center">
            <Link href="/app/dashboard" className="text-sm text-gray-600 hover:text-sky-600">
              Dashboard
            </Link>
            <Link href="/app/shopping-list" className="text-sm text-gray-600 hover:text-sky-600">
              Lista de Compras
            </Link>
            <Link href="/app/settings" className="text-sm text-gray-600 hover:text-sky-600">
              Configuración
            </Link>
            <button
              onClick={handleLogout}
              className="text-sm text-red-600 hover:text-red-700 font-medium"
            >
              Cerrar Sesión
            </button>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-6">{children}</main>
    </div>
  );
}