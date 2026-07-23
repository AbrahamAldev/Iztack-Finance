import Link from "next/link";
import { ArrowRight, Camera, Bot, BarChart3, ShoppingCart, Shield, Sparkles, Check } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[var(--background)]">
      {/* Header */}
      <header className="border-b border-[var(--border)] glass sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl gradient-bg flex items-center justify-center text-white shadow-glow">
              <Sparkles className="h-5 w-5" />
            </div>
            <span className="text-xl font-bold">
              <span className="gradient-text">Iztack</span> Finance
            </span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-[var(--text-secondary)]">
            <a href="#features" className="hover:text-[var(--text)] transition">Funciones</a>
            <a href="#pricing" className="hover:text-[var(--text)] transition">Precios</a>
          </nav>
          <div className="flex items-center gap-3">
            <Link href="/login" className="btn btn-primary text-sm py-2.5 px-5">
              Iniciar sesión
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24 text-center overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-primary-500/10 rounded-full blur-3xl -z-10" />
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-50 dark:bg-primary-500/10 text-primary-700 dark:text-primary-300 text-sm font-medium mb-8 border border-primary-100 dark:border-primary-500/20">
          <Sparkles className="h-4 w-4" /> Nuevo: asistente con IA incluido
        </div>
        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold text-[var(--text)] leading-tight tracking-tight">
          Tu asistente financiero{" "}
          <span className="gradient-text">automatizado</span>
        </h1>
        <p className="mt-6 text-xl text-[var(--text-secondary)] max-w-3xl mx-auto leading-relaxed">
          Captura tickets con una foto, solicita facturas automáticamente, organiza tus gastos por categoría y recibe análisis financieros inteligentes.
        </p>
        <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/register" className="btn btn-primary text-base px-8 py-4">
            Comenzar gratis <ArrowRight className="h-5 w-5" />
          </Link>
          <a href="#features" className="btn btn-secondary text-base px-8 py-4">
            Ver funciones
          </a>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-[var(--text)] mb-4">Todo lo que necesitas para controlar tus finanzas</h2>
          <p className="text-[var(--text-secondary)] max-w-2xl mx-auto">Desde capturar tickets hasta obtener análisis financieros, Iztack-Finance automatiza todo el proceso.</p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => {
            const Icon = f.icon;
            return (
              <div key={i} className="card p-6 group">
                <div className="w-12 h-12 rounded-xl bg-primary-50 dark:bg-primary-500/10 flex items-center justify-center text-primary-600 dark:text-primary-400 mb-4 group-hover:scale-110 transition-transform">
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-bold text-[var(--text)] mb-2">{f.title}</h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{f.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="bg-[var(--surface)] border-y border-[var(--border)] py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-[var(--text)] mb-4">Planes y precios</h2>
            <p className="text-[var(--text-secondary)] max-w-2xl mx-auto">Elige el plan que mejor se adapte a tus necesidades.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {plans.map((p, i) => (
              <div key={i} className={`card p-8 relative ${p.featured ? "ring-2 ring-primary-500" : ""}`}>
                {p.featured && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 text-xs font-bold text-white bg-primary-600 px-4 py-1 rounded-full">
                    MÁS POPULAR
                  </span>
                )}
                <h3 className="text-xl font-bold text-[var(--text)]">{p.name}</h3>
                <p className="text-4xl font-extrabold text-[var(--text)] mt-4">
                  ${p.price}<span className="text-base font-normal text-[var(--text-muted)]">/mes</span>
                </p>
                <p className="text-sm text-[var(--text-secondary)] mt-2">{p.desc}</p>
                <ul className="mt-6 space-y-3">
                  {p.features.map((f, j) => (
                    <li key={j} className="text-sm text-[var(--text-secondary)] flex items-start gap-2">
                      <Check className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" /> {f}
                    </li>
                  ))}
                </ul>
                <Link href="/register" className={`mt-8 block text-center py-3 rounded-xl font-semibold text-sm transition ${p.featured ? "btn btn-primary" : "btn btn-secondary"}`}>
                  Comenzar prueba gratis
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
        <h2 className="text-3xl sm:text-4xl font-bold text-[var(--text)] mb-4">¿Listo para automatizar tus finanzas?</h2>
        <p className="text-[var(--text-secondary)] mb-8 max-w-xl mx-auto">Captura tu primer ticket en menos de 30 segundos. Sin configuración complicada.</p>
        <Link href="/register" className="btn btn-primary text-base px-8 py-4">
          Crear cuenta gratis <ArrowRight className="h-5 w-5" />
        </Link>
      </section>

      {/* Footer */}
      <footer className="border-t border-[var(--border)] bg-[var(--surface)] py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-[var(--text-muted)]">
          <p>© 2026 Iztack-Finance. Todos los derechos reservados.</p>
        </div>
      </footer>
    </div>
  );
}

const features = [
  { icon: Camera, title: "Captura inteligente", desc: "Toma una foto de tu ticket y el sistema extrae automáticamente todos los datos: tienda, fecha, productos y total." },
  { icon: Bot, title: "Facturación automática", desc: "El bot accede al portal de cada tienda y solicita la factura CFDI por ti. Solo tomas la foto." },
  { icon: BarChart3, title: "Dashboard inteligente", desc: "Visualiza tus gastos en tiempo real con gráficos interactivos y recomendaciones de ahorro." },
  { icon: ShoppingCart, title: "Lista de compras automática", desc: "Detecta tus ciclos de consumo y genera listas inteligentes para toda la familia." },
  { icon: Shield, title: "Alertas de garantía", desc: "Te avisamos cuando un producto está por vencer su garantía. Nunca pierdas la oportunidad de reclamar." },
  { icon: Sparkles, title: "Almacenamiento en la nube", desc: "Todas tus facturas en PDF y XML se guardan automáticamente en Google Drive, organizadas por tienda y año." },
];

const plans = [
  {
    name: "Básico",
    price: 0,
    desc: "Para empezar a organizar tus finanzas personales.",
    features: ["Captura de tickets (hasta 10/mes)", "Dashboard financiero básico", "Almacenamiento en Google Drive", "Soporte por email"],
    featured: false,
  },
  {
    name: "Pro",
    price: 149,
    desc: "Para quienes quieren automatizar completamente sus finanzas.",
    features: ["Captura de tickets ilimitada", "Facturación automática", "Lista de compras inteligente", "Análisis financiero avanzado", "Gestión de garantías", "Soporte prioritario"],
    featured: true,
  },
  {
    name: "Familiar",
    price: 299,
    desc: "Para familias que quieren gestionar sus finanzas juntas.",
    features: ["Todo lo del plan Pro", "Hasta 5 miembros", "Aprobación familiar de compras", "Listas de compras compartidas", "Reportes consolidados", "Soporte 24/7"],
    featured: false,
  },
];
