import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-sky-50">
      {/* ===== HEADER ===== */}
      <header className="border-b border-gray-100 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🏦</span>
            <span className="text-xl font-bold text-sky-600">Iztack-Finance</span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm text-gray-600">
            <a href="#features" className="hover:text-sky-600 transition">Funciones</a>
            <a href="#pricing" className="hover:text-sky-600 transition">Precios</a>
            <a href="#docs" className="hover:text-sky-600 transition">Documentación</a>
          </nav>
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="px-5 py-2.5 text-sm font-semibold text-white bg-sky-600 rounded-lg hover:bg-sky-700 shadow-sm hover:shadow-md transition-all"
            >
              Iniciar Sesión
            </Link>
          </div>
        </div>
      </header>

      {/* ===== HERO ===== */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center">
        <div className="text-6xl mb-6">🏦</div>
        <h1 className="text-5xl sm:text-6xl font-extrabold text-gray-900 leading-tight">
          Tu asistente financiero{" "}
          <span className="text-sky-600">automatizado</span>
        </h1>
        <p className="mt-6 text-xl text-gray-500 max-w-3xl mx-auto leading-relaxed">
          Captura tickets con una foto, solicita facturas automáticamente en los portales de cada tienda,
          organiza tus gastos por categoría y recibe análisis financieros inteligentes.
        </p>
        <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/register"
            className="px-8 py-3.5 text-base font-semibold text-white bg-sky-600 rounded-xl hover:bg-sky-700 shadow-lg hover:shadow-xl transition-all"
          >
            Comenzar Gratis
          </Link>
          <a
            href="#features"
            className="px-8 py-3.5 text-base font-semibold text-gray-700 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-all"
          >
            Ver Funciones
          </a>
        </div>
      </section>

      {/* ===== FEATURES ===== */}
      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">
          Todo lo que necesitas para controlar tus finanzas
        </h2>
        <p className="text-center text-gray-500 mb-12 max-w-2xl mx-auto">
          Desde capturar tickets hasta obtener análisis financieros, Iztack-Finance automatiza todo el proceso.
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((f, i) => (
            <div key={i} className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition">
              <div className="text-3xl mb-4">{f.icon}</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{f.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ===== PRICING ===== */}
      <section id="pricing" className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">
            Planes y Precios
          </h2>
          <p className="text-center text-gray-500 mb-12 max-w-2xl mx-auto">
            Elige el plan que mejor se adapte a tus necesidades. Todos los planes incluyen 14 días de prueba gratis.
          </p>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {plans.map((p, i) => (
              <div
                key={i}
                className={`rounded-2xl p-8 border ${
                  p.featured
                    ? "border-sky-500 ring-2 ring-sky-500 bg-sky-50"
                    : "border-gray-200 bg-white"
                }`}
              >
                {p.featured && (
                  <span className="text-xs font-semibold text-sky-600 bg-sky-100 px-3 py-1 rounded-full">
                    MÁS POPULAR
                  </span>
                )}
                <h3 className="text-xl font-bold text-gray-900 mt-3">{p.name}</h3>
                <p className="text-3xl font-extrabold text-gray-900 mt-4">
                  ${p.price}
                  <span className="text-base font-normal text-gray-500">/mes</span>
                </p>
                <p className="text-sm text-gray-500 mt-2">{p.desc}</p>
                <ul className="mt-6 space-y-3">
                  {p.features.map((f, j) => (
                    <li key={j} className="text-sm text-gray-600 flex items-start gap-2">
                      <span className="text-sky-500 mt-0.5">✓</span>
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/register"
                  className={`mt-8 block text-center py-3 rounded-xl font-semibold text-sm transition ${
                    p.featured
                      ? "bg-sky-600 text-white hover:bg-sky-700"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  Comenzar Prueba Gratis
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== DOCS / CTA ===== */}
      <section id="docs" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          ¿Listo para automatizar tus finanzas?
        </h2>
        <p className="text-gray-500 mb-8 max-w-xl mx-auto">
          Captura tu primer ticket en menos de 30 segundos. Sin configuración complicada.
        </p>
        <Link
          href="/register"
          className="inline-block px-8 py-3.5 text-base font-semibold text-white bg-sky-600 rounded-xl hover:bg-sky-700 shadow-lg transition-all"
        >
          Crear Cuenta Gratis
        </Link>
      </section>

      {/* ===== FOOTER ===== */}
      <footer className="border-t border-gray-100 bg-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-400">
          <p>© 2026 Iztack-Finance. Todos los derechos reservados.</p>
        </div>
      </footer>
    </div>
  );
}

const features = [
  {
    icon: "📸",
    title: "Captura Inteligente",
    desc: "Toma una foto de tu ticket y el sistema extrae automáticamente todos los datos: tienda, fecha, productos, total.",
  },
  {
    icon: "🤖",
    title: "Facturación Automática",
    desc: "El bot accede al portal de cada tienda con tus credenciales y solicita la factura por ti. Sin hacer nada.",
  },
  {
    icon: "📊",
    title: "Dashboard Financiero",
    desc: "Visualiza tus gastos por categoría, detecta fugas de dinero y recibe recomendaciones personalizadas.",
  },
  {
    icon: "🛒",
    title: "Lista de Compras Inteligente",
    desc: "El sistema detecta tus ciclos de consumo y genera listas de compras automáticas. Comparte y aprueba en familia.",
  },
  {
    icon: "🔧",
    title: "Gestión de Garantías",
    desc: "Los productos con garantía se almacenan en una carpeta especial. Encuentra tu ticket de garantía en segundos.",
  },
  {
    icon: "☁️",
    title: "Almacenamiento en la Nube",
    desc: "Todas tus facturas en PDF y XML se guardan automáticamente en Google Drive, organizadas por tienda y tipo.",
  },
  {
    icon: "📱",
    title: "Multi-plataforma",
    desc: "Accede desde la web o envía tus tickets por Telegram. El bot te responde al instante.",
  },
  {
    icon: "🔒",
    title: "Privacidad Total",
    desc: "Tus datos están cifrados y aislados por usuario. Nadie más puede ver tu información financiera.",
  },
  {
    icon: "📈",
    title: "Análisis Predictivo",
    desc: "Recibe alertas de fugas de dinero, sugerencias de ahorro y predicciones de gastos futuros.",
  },
];

const plans = [
  {
    name: "Básico",
    price: 0,
    desc: "Para empezar a organizar tus finanzas personales.",
    features: [
      "Captura de tickets (hasta 10/mes)",
      "Dashboard financiero básico",
      "Almacenamiento en Google Drive",
      "Soporte por email",
    ],
    featured: false,
  },
  {
    name: "Pro",
    price: 149,
    desc: "Para quienes quieren automatizar completamente sus finanzas.",
    features: [
      "Captura de tickets ilimitada",
      "Facturación automática en todos los portales",
      "Lista de compras inteligente",
      "Análisis financiero avanzado",
      "Gestión de garantías",
      "Soporte prioritario",
    ],
    featured: true,
  },
  {
    name: "Familiar",
    price: 299,
    desc: "Para familias que quieren gestionar sus finanzas juntos.",
    features: [
      "Todo lo del plan Pro",
      "Hasta 5 miembros",
      "Aprobación familiar de compras",
      "Listas de compras compartidas",
      "Reportes consolidados",
      "Soporte 24/7",
    ],
    featured: false,
  },
];