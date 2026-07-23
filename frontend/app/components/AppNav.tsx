"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Menu, X, LogOut, Wallet, LayoutDashboard, ShoppingCart, Settings, HardDrive } from "lucide-react";
import ChatWidget from "./ChatWidget";
import ThemeToggle from "./ThemeToggle";

export default function AppNav() {
  const router = useRouter();
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);

  function handleLogout() {
    localStorage.removeItem("iztack_token");
    router.push("/login");
  }

  const links = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/shopping-list", label: "Lista de compras", icon: ShoppingCart },
    { href: "/storage", label: "Almacenamiento", icon: HardDrive },
    { href: "/settings", label: "Configuración", icon: Settings },
  ];

  return (
    <>
      <nav className="sticky top-0 z-30 glass border-b border-[var(--border)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">
            <Link href="/dashboard" className="flex items-center gap-2.5 shrink-0 group">
              <div className="w-9 h-9 rounded-xl gradient-bg flex items-center justify-center shadow-glow group-hover:scale-105 transition-transform">
                <Wallet className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold">
                <span className="gradient-text">Iztack</span>
              </span>
            </Link>

            {/* Desktop nav */}
            <div className="hidden md:flex items-center gap-1">
              {links.map((l) => {
                const Icon = l.icon;
                const active = pathname === l.href;
                return (
                  <Link
                    key={l.href}
                    href={l.href}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                      active
                        ? "bg-primary-50 dark:bg-primary-500/15 text-primary-700 dark:text-primary-300"
                        : "text-[var(--text-secondary)] hover:text-[var(--text)] hover:bg-[var(--surface-elevated)]"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    {l.label}
                  </Link>
                );
              })}
            </div>

            <div className="hidden md:flex items-center gap-2">
              <ThemeToggle />
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-xl transition-colors"
              >
                <LogOut className="h-4 w-4" />
                Salir
              </button>
            </div>

            {/* Mobile hamburger */}
            <div className="flex md:hidden items-center gap-2">
              <ThemeToggle />
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="p-2 rounded-xl text-[var(--text)] hover:bg-[var(--surface-elevated)]"
              >
                {menuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden border-t border-[var(--border)] bg-[var(--surface)] animate-fade-in">
            <div className="px-4 py-3 space-y-1">
              {links.map((l) => {
                const Icon = l.icon;
                const active = pathname === l.href;
                return (
                  <Link
                    key={l.href}
                    href={l.href}
                    onClick={() => setMenuOpen(false)}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium ${
                      active
                        ? "bg-primary-50 dark:bg-primary-500/15 text-primary-700 dark:text-primary-300"
                        : "text-[var(--text-secondary)] hover:bg-[var(--surface-elevated)]"
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    {l.label}
                  </Link>
                );
              })}
              <button
                onClick={handleLogout}
                className="flex w-full items-center gap-3 px-3 py-2.5 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-xl"
              >
                <LogOut className="h-5 w-5" />
                Cerrar sesión
              </button>
            </div>
          </div>
        )}
      </nav>
      <ChatWidget />
    </>
  );
}
