"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import ChatWidget from "./ChatWidget";

export default function AppNav() {
  const router = useRouter();
  const pathname = usePathname();

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
          <Link href="/dashboard" className="text-xl font-bold text-sky-600">
            🏦 Iztack-Finance
          </Link>
          <div className="flex gap-4 items-center">
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
        </div>
      </nav>
      <ChatWidget />
    </>
  );
}
