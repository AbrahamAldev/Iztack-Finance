"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import AuthGuard from "../components/AuthGuard";
import AppNav from "../components/AppNav";
import TicketUpload from "../components/TicketUpload";
import {
  TrendingUp,
  Receipt,
  FileWarning,
  ShieldCheck,
  Camera,
  ArrowUpRight,
  Store,
  PieChart,
  Activity,
  Zap,
  Settings,
  ShoppingCart,
  HardDrive,
  ExternalLink,
} from "lucide-react";

interface DashboardData {
  kpi: {
    monthly_spent: number;
    avg_ticket: number;
    pending_invoices: number;
    active_warranties: number;
  };
  storage: {
    used_bytes: number;
    max_bytes: number;
    used_pct: number;
    free_bytes: number;
  };
  recent_tickets: Array<{
    id: string;
    store_name: string;
    total_amount: number;
    purchase_date: string;
    status: string;
    has_warranty: boolean;
    product_count: number;
  }>;
  charts: {
    by_category: Array<{ category: string; amount: number }>;
    by_store: Array<{ store: string; amount: number }>;
  };
}

function formatCurrency(n?: number) {
  if (n === undefined || n === null) return "$0.00";
  return "$" + n.toLocaleString("es-MX", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function KpiCard({
  title,
  value,
  icon: Icon,
  trend,
  color,
}: {
  title: string;
  value: string;
  icon: any;
  trend?: React.ReactNode;
  color: "blue" | "emerald" | "amber" | "rose";
}) {
  const gradients: Record<string, string> = {
    blue: "from-blue-500 to-indigo-600",
    emerald: "from-emerald-500 to-teal-600",
    amber: "from-amber-500 to-orange-600",
    rose: "from-rose-500 to-pink-600",
  };
  return (
    <div className="card p-6 flex items-start justify-between group">
      <div>
        <p className="text-sm font-medium text-[var(--text-muted)] mb-1">{title}</p>
        <p className="text-2xl sm:text-3xl font-bold text-[var(--text)]">{value}</p>
        {trend && <p className="text-xs text-[var(--text-muted)] mt-2 flex items-center gap-1">{trend}</p>}
      </div>
      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${gradients[color]} flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-transform`}>
        <Icon className="h-6 w-6" />
      </div>
    </div>
  );
}

function BarChart({ data, labelKey }: { data: Array<{ category?: string; store?: string; amount: number }>; labelKey: "category" | "store" }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-[var(--text-muted)]">
        <PieChart className="h-10 w-10 mb-3 opacity-40" />
        <p className="text-sm">Sin datos este mes</p>
        <p className="text-xs opacity-70">Sube tu primer ticket para ver análisis</p>
      </div>
    );
  }
  const max = Math.max(...data.map((d) => d.amount), 1);
  return (
    <div className="space-y-4">
      {data.map((item, idx) => {
        const label = (item[labelKey] as string) || "Otro";
        const pct = (item.amount / max) * 100;
        return (
          <div key={idx} className="group">
            <div className="flex justify-between text-sm mb-1.5">
              <span className="font-medium text-[var(--text)] capitalize truncate max-w-[60%]">{label}</span>
              <span className="font-semibold text-[var(--text-secondary)]">{formatCurrency(item.amount)}</span>
            </div>
            <div className="h-2.5 w-full bg-[var(--surface-elevated)] rounded-full overflow-hidden border border-[var(--border)]">
              <div
                className="h-full rounded-full bg-gradient-to-r from-primary-500 to-indigo-500 transition-all duration-700 ease-out"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function DashboardContent() {
  const [showUpload, setShowUpload] = useState(false);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  async function fetchDashboard() {
    const token = localStorage.getItem("iztack_token");
    if (!token) return;
    try {
      const res = await fetch("/api/dashboard/overview", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (e) {
      console.error("Error fetching dashboard:", e);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-16 h-16 rounded-2xl gradient-bg flex items-center justify-center mx-auto mb-4 animate-pulse">
            <Activity className="h-8 w-8 text-white" />
          </div>
          <p className="text-[var(--text-secondary)]">Cargando tu dashboard...</p>
        </div>
      </div>
    );
  }

  const kpi = data?.kpi;

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8 animate-slide-up">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-[var(--text)]">Dashboard</h1>
          <p className="text-[var(--text-secondary)] text-sm mt-1">
            Resumen de tus finanzas personales
          </p>
        </div>
        <button
          onClick={() => setShowUpload(true)}
          className="btn btn-primary px-6 py-3"
        >
          <Camera className="h-5 w-5" />
          <span>Subir ticket</span>
        </button>
      </div>

      {showUpload && (
        <TicketUpload onClose={() => { setShowUpload(false); fetchDashboard(); }} />
      )}

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <KpiCard
          title="Gastos del mes"
          value={formatCurrency(kpi?.monthly_spent)}
          icon={TrendingUp}
          trend={<><ArrowUpRight className="h-3 w-3" /> Acumulado mensual</>}
          color="blue"
        />
        <KpiCard
          title="Ticket promedio"
          value={formatCurrency(kpi?.avg_ticket)}
          icon={Receipt}
          color="emerald"
        />
        <KpiCard
          title="Facturas pendientes"
          value={(kpi?.pending_invoices || 0).toString()}
          icon={FileWarning}
          color="amber"
        />
        <KpiCard
          title="Garantías activas"
          value={(kpi?.active_warranties || 0).toString()}
          icon={ShieldCheck}
          color="rose"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Recent tickets */}
        <div className="card p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-bold text-[var(--text)] flex items-center gap-2">
              <Receipt className="h-5 w-5 text-primary-500" />
              Tickets recientes
            </h2>
            <button
              onClick={() => setShowUpload(true)}
              className="text-sm font-medium text-primary-600 dark:text-primary-400 hover:underline"
            >
              + Nuevo
            </button>
          </div>

          {data?.recent_tickets && data.recent_tickets.length > 0 ? (
            <div className="divide-y divide-[var(--border)]">
              {data.recent_tickets.map((t) => (
                <div key={t.id} className="py-4 flex items-center justify-between group hover:bg-[var(--surface-elevated)]/50 -mx-2 px-2 rounded-xl transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary-50 dark:bg-primary-500/10 flex items-center justify-center text-primary-600 dark:text-primary-400">
                      <Store className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="font-semibold text-[var(--text)]">{t.store_name}</p>
                      <p className="text-xs text-[var(--text-muted)]">
                        {t.purchase_date} · {t.product_count} producto(s)
                        {t.has_warranty && " · 🔧 Garantía"}
                      </p>
                    </div>
                  </div>
                  <p className="font-bold text-[var(--text)]">{formatCurrency(t.total_amount)}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 rounded-2xl bg-primary-50 dark:bg-primary-500/10 flex items-center justify-center mx-auto mb-4">
                <Camera className="h-8 w-8 text-primary-500" />
              </div>
              <p className="text-[var(--text)] font-medium mb-1">No hay tickets aún</p>
              <p className="text-sm text-[var(--text-muted)] mb-4">Sube tu primer ticket para verlo aquí.</p>
              <button onClick={() => setShowUpload(true)} className="btn btn-primary">
                Subir ticket
              </button>
            </div>
          )}
        </div>

        {/* Status & quick actions */}
        <div className="space-y-6">
          <div className="card p-6">
            <h3 className="font-bold text-[var(--text)] mb-4 flex items-center gap-2">
              <Zap className="h-5 w-5 text-amber-500" />
              Conexiones
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2">
                <span className="text-sm text-[var(--text-secondary)]">API Backend</span>
                <span className="badge badge-success">● Activo</span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm text-[var(--text-secondary)]">Base de datos</span>
                <span className="badge badge-success">● Conectada</span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm text-[var(--text-secondary)]">Bot Telegram</span>
                <span className="badge badge-warning">● Configurar</span>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h3 className="font-bold text-[var(--text)] mb-4 flex items-center gap-2">
              <HardDrive className="h-5 w-5 text-primary-500" />
              Almacenamiento
            </h3>
            {data?.storage ? (
              <>
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-[var(--text-secondary)]">
                    {(data.storage.used_bytes / 1024 / 1024).toFixed(1)} MB / {(data.storage.max_bytes / 1024 / 1024 / 1024).toFixed(1)} GB
                  </span>
                  <span className={`font-semibold ${data.storage.used_pct > 80 ? "text-rose-500" : data.storage.used_pct > 50 ? "text-amber-500" : "text-emerald-500"}`}>
                    {data.storage.used_pct}%
                  </span>
                </div>
                <div className="h-2.5 w-full bg-[var(--surface-elevated)] rounded-full overflow-hidden border border-[var(--border)] mb-4">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      data.storage.used_pct > 80
                        ? "bg-gradient-to-r from-rose-500 to-pink-500"
                        : data.storage.used_pct > 50
                        ? "bg-gradient-to-r from-amber-500 to-orange-500"
                        : "bg-gradient-to-r from-emerald-500 to-teal-500"
                    }`}
                    style={{ width: `${Math.min(data.storage.used_pct, 100)}%` }}
                  />
                </div>
                <Link
                  href="/storage"
                  className="flex items-center gap-2 p-3 rounded-xl hover:bg-[var(--surface-elevated)] transition-colors text-[var(--text-secondary)] hover:text-[var(--text)] text-sm"
                >
                  <ExternalLink className="h-4 w-4" />
                  <span className="font-medium">Administrar almacenamiento</span>
                </Link>
              </>
            ) : (
              <p className="text-sm text-[var(--text-muted)]">Cargando...</p>
            )}
          </div>

          <div className="card p-6">
            <h3 className="font-bold text-[var(--text)] mb-3">Accesos rápidos</h3>
            <div className="space-y-2">
              <Link href="/settings" className="flex items-center gap-3 p-3 rounded-xl hover:bg-[var(--surface-elevated)] transition-colors text-[var(--text-secondary)] hover:text-[var(--text)]">
                <Settings className="h-5 w-5" />
                <span className="text-sm font-medium">Configuración</span>
              </Link>
              <Link href="/shopping-list" className="flex items-center gap-3 p-3 rounded-xl hover:bg-[var(--surface-elevated)] transition-colors text-[var(--text-secondary)] hover:text-[var(--text)]">
                <ShoppingCart className="h-5 w-5" />
                <span className="text-sm font-medium">Lista de compras</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-lg font-bold text-[var(--text)] mb-5 flex items-center gap-2">
            <PieChart className="h-5 w-5 text-primary-500" />
            Gastos por categoría
          </h2>
          <BarChart data={data?.charts?.by_category || []} labelKey="category" />
        </div>
        <div className="card p-6">
          <h2 className="text-lg font-bold text-[var(--text)] mb-5 flex items-center gap-2">
            <Store className="h-5 w-5 text-primary-500" />
            Gastos por tienda
          </h2>
          <BarChart data={data?.charts?.by_store || []} labelKey="store" />
        </div>
      </div>
    </main>
  );
}

export default function DashboardPage() {
  return (
    <AuthGuard>
      <AppNav />
      <DashboardContent />
    </AuthGuard>
  );
}
