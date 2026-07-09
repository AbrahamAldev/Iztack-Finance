"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Menu, X } from "lucide-react";
import ChatWidget from "./ChatWidget";

export default function AppNav() {
  const router = useRouter();
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);

  function handleLogout() {
    localStorage.removeItem("iztack_token");
    router.push("/login");
  }

  const links = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/shopping-list", label: "Lista de Compras" },
    { href: "/settings", label: "Configuración" },
  ];

  return (
    <>
      <nav className="bg-white border-b border-gray-200 px-4 py-3 mb-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/dashboard" className="text-xl font-bold text-sky-600 shrink-0">
            🏦 Iztack
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex gap-4 items-center">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className={`text-sm ${
                  pathname === l.href
                    ? "text-sky-600 font-semibold"
                    : "text-gray-600 hover:text-sky-600"
                }`}
              >
                {l.label}
              </Link>
            ))}
            <button
              onClick={handleLogout}
              className="text-sm text-red-600 hover:text-red-700 font-medium"
            >
              Cerrar Sesión
            </button>
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden p-1 text-gray-600"
          >
            {menuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden mt-3 pt-3 border-t border-gray-100 space-y-2">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                onClick={() => setMenuOpen(false)}
                className={`block px-2 py-2 rounded text-sm ${
                  pathname === l.href
                    ? "text-sky-600 font-semibold bg-sky-50"
                    : "text-gray-600 hover:bg-gray-50"
                }`}
              >
                {l.label}
              </Link>
            ))}
            <button
              onClick={handleLogout}
              className="block w-full text-left px-2 py-2 text-sm text-red-600 hover:bg-red-50 rounded"
            >
              Cerrar Sesión
            </button>
          </div>
        )}
      </nav>
      <ChatWidget />
    </>
  );
}