import Link from 'next/link'

export default function Home() {
  return (
    <div className="space-y-8">
      <div className="text-center py-12">
        <h1 className="text-4xl font-bold text-sky-600 mb-4">🏦 Sistema Financiero</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Tu asistente financiero personal. Captura tickets, solicita facturas automáticamente, 
          organiza tus gastos y recibe análisis inteligentes.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link href="/dashboard" className="card hover:ring-2 hover:ring-sky-400 transition-all">
          <div className="text-3xl mb-3">📊</div>
          <h2 className="text-lg font-semibold">Dashboard Financiero</h2>
          <p className="text-sm text-gray-500 mt-2">
            Visualiza tus gastos por categoría, detecta fugas de dinero y recibe recomendaciones.
          </p>
          <div className="mt-4 flex gap-2">
            <span className="badge badge-info">Gastos</span>
            <span className="badge badge-info">Análisis</span>
          </div>
        </Link>

        <Link href="/shopping-list" className="card hover:ring-2 hover:ring-sky-400 transition-all">
          <div className="text-3xl mb-3">🛒</div>
          <h2 className="text-lg font-semibold">Lista de Compras</h2>
          <p className="text-sm text-gray-500 mt-2">
            Listas inteligentes basadas en tus ciclos de consumo. Comparte y aprueba en familia.
          </p>
          <div className="mt-4 flex gap-2">
            <span className="badge badge-success">Automática</span>
            <span className="badge badge-info">Familiar</span>
          </div>
        </Link>

        <Link href="/settings" className="card hover:ring-2 hover:ring-sky-400 transition-all">
          <div className="text-3xl mb-3">⚙️</div>
          <h2 className="text-lg font-semibold">Configuración</h2>
          <p className="text-sm text-gray-500 mt-2">
            Administra tus cuentas, credenciales de tiendas y preferencias del sistema.
          </p>
          <div className="mt-4 flex gap-2">
            <span className="badge badge-warning">Cuentas</span>
            <span className="badge badge-info">Preferencias</span>
          </div>
        </Link>
      </div>
    </div>
  )
}