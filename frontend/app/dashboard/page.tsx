"use client";

import { useState, useEffect } from "react";
import AuthGuard from "../components/AuthGuard";
import AppNav from "../components/AppNav";
import TicketUpload from "../components/TicketUpload";

interface DashboardData {
  kpi: {
    monthly_spent: number;
    avg_ticket: number;
    pending_invoices: number;
    active_warranties: number;
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
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-4xl animate-pulse mb-4">🏦</div>
          <p className="text-gray-500">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  const kpi = data?.kpi;

  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">Dashboard</h1>
          <p className="text-sm text-gray-500">
            Resumen de tus finanzas y estado del sistema
          </p>
        </div>
        <button
          onClick={() => setShowUpload(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-sky-600 text-white rounded-lg font-medium hover:bg-sky-700 shadow-sm transition-all"
        >
          <span className="text-lg">📸</span>
          Subir Ticket
        </button>
      </div>

      {showUpload && <TicketUpload onClose={() => { setShowUpload(false); fetchDashboard(); }} />}

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-500 mb-1">Gastos del Mes</p>
          <p className="text-2xl font-bold text-gray-900">
            ${kpi?.monthly_spent?.toFixed(2) || "0.00"}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-500 mb-1">Ticket Promedio</p>
          <p className="text-2xl font-bold text-gray-900">
            ${kpi?.avg_ticket?.toFixed(2) || "0.00"}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-500 mb-1">Facturas Pendientes</p>
          <p className={`text-2xl font-bold ${(kpi?.pending_invoices || 0) > 0 ? "text-yellow-600" : "text-green-600"}`}>
            {kpi?.pending_invoices || 0}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-500 mb-1">Garantías Activas</p>
          <p className={`text-2xl font-bold ${(kpi?.active_warranties || 0) > 0 ? "text-green-600" : "text-gray-900"}`}>
            {kpi?.active_warranties || 0}
          </p>
        </div>
      </div>

      {/* Recent Tickets */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Tickets Recientes</h2>
        {data?.recent_tickets && data.recent_tickets.length > 0 ? (
          <div className="space-y-3">
            {data.recent_tickets.map((t) => (
              <div key={t.id} className="flex items-center justify-between py-2 border-b last:border-0">
                <div>
                  <p className="font-medium text-gray-900">{t.store_name}</p>
                  <p className="text-sm text-gray-500">
                    {t.purchase_date} · {t.product_count} producto(s)
                    {t.has_warranty && " · 🔧 Garantía"}
                  </p>
                </div>
                <p className="font-semibold text-gray-900">${t.total_amount.toFixed(2)}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-400">
            <p className="text-4xl mb-2">📸</p>
            <p>No hay tickets aún. Sube tu primer ticket para verlo aquí.</p>
          </div>
        )}
      </div>

      {/* Spending by Category */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Gastos por Categoría</h2>
          {data?.charts?.by_category && data.charts.by_category.length > 0 ? (
            <div className="space-y-2">
              {data.charts.by_category.map((c) => (
                <div key={c.category} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 capitalize">{c.category}</span>
                  <span className="text-sm font-semibold">${c.amount.toFixed(2)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400 text-center py-4">Sin datos este mes</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Gastos por Tienda</h2>
          {data?.charts?.by_store && data.charts.by_store.length > 0 ? (
            <div className="space-y-2">
              {data.charts.by_store.map((s) => (
                <div key={s.store} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{s.store}</span>
                  <span className="text-sm font-semibold">${s.amount.toFixed(2)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400 text-center py-4">Sin datos este mes</p>
          )}
        </div>
      </div>

      {/* Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Conexiones</h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">API Backend</span>
              <span className="text-sm text-green-600 font-medium">● Activo</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Base de Datos</span>
              <span className="text-sm text-green-600 font-medium">● Conectada</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Bot Telegram</span>
              <span className="text-sm text-yellow-600 font-medium">● Configurar</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Accesos Rápidos</h3>
          <div className="space-y-2">
            <a href="/settings" className="block text-sm text-blue-600 hover:underline">
              → Configuración
            </a>
            <a href="/shopping-list" className="block text-sm text-blue-600 hover:underline">
              → Lista de Compras
            </a>
          </div>
        </div>
      </div>
    </>
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