import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Iztack-Finance',
  description: 'Dashboard de finanzas personales - Gestión de tickets, facturas y gastos',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es-MX">
      <body>
        {children}
      </body>
    </html>
  )
}