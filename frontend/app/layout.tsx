import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Sistema Financiero',
  description: 'Dashboard de finanzas personales - Gestión de tickets, facturas y gastos',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es-MX">
      <body>
        <nav className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <a href="/" className="text-xl font-bold text-sky-600">🏦 Sistema Financiero</a>
            <div className="flex gap-4">
              <a href="/dashboard" className="text-sm text-gray-600 hover:text-sky-600">Dashboard</a>
              <a href="/shopping-list" className="text-sm text-gray-600 hover:text-sky-600">Lista de Compras</a>
              <a href="/settings" className="text-sm text-gray-600 hover:text-sky-600">Configuración</a>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 py-6">
          {children}
        </main>
      </body>
    </html>
  )
}