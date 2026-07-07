"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("iztack_token");
    setIsAuthenticated(!!token);
    if (token) {
      // Decode JWT payload (base64) to get email
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        setUserEmail(payload.sub || null);
      } catch {
        setUserEmail(null);
      }
    }
  }, [pathname]);

  function handleLogout() {
    localStorage.removeItem("iztack_token");
    router.push("/login");
  }

  // Don't show navbar on auth pages
  if (pathname === "/login" || pathname === "/register") {
    return null;
  }

  return (
    <nav className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-sky-600">
          🏦 Iztack-Finance
        </Link>
        <div className="flex gap-4 items-center">
          <Link href="/dashboard" className="text-sm text-gray-600 hover:text-sky-600">
            Dashboard
          </Link>
          <Link href="/shopping-list" className="text-sm text-gray-600 hover:text-sky-600">
            Lista de Compras
          </Link>
          <Link href="/settings" className="text-sm text-gray-600 hover:text-sky-600">
            Configuración
          </Link>
          {isAuthenticated ? (
            <button
              onClick={handleLogout}
              className="text-sm text-red-600 hover:text-red-700 font-medium"
            >
              Cerrar Sesión
            </button>
          ) : (
            <Link href="/login" className="text-sm text-sky-600 hover:text-sky-700 font-medium">
              Iniciar Sesión
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}