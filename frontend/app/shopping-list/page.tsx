"use client";

import { useState, useEffect } from "react";
import AuthGuard from "../components/AuthGuard";
import AppNav from "../components/AppNav";
import { ShoppingCart, RefreshCw, Printer, Package, Store, Loader2 } from "lucide-react";

interface ShoppingItem {
  name: string;
  category?: string;
  quantity: number;
  unit?: string;
  estimated_price?: number;
  preferred_store?: string;
  priority?: string;
}

interface ShoppingListData {
  id?: string;
  title?: string;
  items?: ShoppingItem[];
  estimated_total?: number;
  store_grouping?: Record<string, ShoppingItem[]>;
  created_at?: string;
  source?: string;
}

function ShoppingListContent() {
  const [data, setData] = useState<ShoppingListData | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchList();
  }, []);

  async function fetchList() {
    const token = localStorage.getItem("iztack_token");
    if (!token) return;
    setLoading(true);
    try {
      const res = await fetch("/api/shopping-list/", { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) {
        setData(await res.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function generateNew() {
    const token = localStorage.getItem("iztack_token");
    if (!token) return;
    setGenerating(true);
    try {
      const res = await fetch("/api/shopping-list/generate", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setData(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setGenerating(false);
    }
  }

  if (loading) {
    return (
      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-10 w-10 text-primary-500 animate-spin" />
        </div>
      </main>
    );
  }

  const items = data?.items || [];
  const grouped = data?.store_grouping || {};
  const hasData = items.length > 0;

  return (
    <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 animate-slide-up">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-[var(--text)]">Lista de compras</h1>
          <p className="text-[var(--text-secondary)] text-sm mt-1">Generada automáticamente según tus ciclos de consumo.</p>
        </div>
        <div className="flex gap-3">
          <button onClick={generateNew} disabled={generating} className="btn btn-primary">
            {generating ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            Regenerar
          </button>
          <button className="btn btn-secondary">
            <Printer className="h-4 w-4" /> Imprimir
          </button>
        </div>
      </div>

      {!hasData ? (
        <div className="card p-12 text-center">
          <div className="w-20 h-20 rounded-2xl bg-primary-50 dark:bg-primary-500/10 flex items-center justify-center mx-auto mb-5">
            <ShoppingCart className="h-10 w-10 text-primary-500" />
          </div>
          <h2 className="text-xl font-bold text-[var(--text)] mb-2">Aún no hay lista de compras</h2>
          <p className="text-[var(--text-secondary)] max-w-md mx-auto mb-6">
            Sube algunos tickets primero. El sistema detectará patrones de consumo y generará tu lista automáticamente.
          </p>
          <button onClick={generateNew} disabled={generating} className="btn btn-primary">
            {generating ? "Generando..." : "Generar lista ahora"}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="card p-6">
              <div className="flex items-center justify-between mb-5">
                <h2 className="text-lg font-bold text-[var(--text)] flex items-center gap-2">
                  <Package className="h-5 w-5 text-primary-500" />
                  {data?.title || "Lista de compras"}
                </h2>
                <span className="text-sm text-[var(--text-muted)]">{items.length} artículos</span>
              </div>
              <div className="divide-y divide-[var(--border)]">
                {items.map((item, idx) => (
                  <div key={idx} className="py-4 flex items-center justify-between group hover:bg-[var(--surface-elevated)]/50 -mx-2 px-2 rounded-xl transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-primary-50 dark:bg-primary-500/10 flex items-center justify-center text-primary-600 dark:text-primary-400 font-semibold text-sm">
                        {item.quantity}
                      </div>
                      <div>
                        <p className="font-semibold text-[var(--text)]">{item.name}</p>
                        <p className="text-xs text-[var(--text-muted)] capitalize">{item.category || "general"} · {item.unit || "pza"}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-[var(--text)]">${(item.estimated_price || 0).toFixed(2)}</p>
                      {item.priority && <span className="text-[10px] uppercase tracking-wide text-[var(--text-muted)]">{item.priority}</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="card p-6">
              <h3 className="font-bold text-[var(--text)] mb-4 flex items-center gap-2">
                <Store className="h-5 w-5 text-primary-500" />
                Por tienda
              </h3>
              <div className="space-y-4">
                {Object.entries(grouped).map(([store, storeItems]) => (
                  <div key={store} className="bg-[var(--surface-elevated)] rounded-xl p-3">
                    <p className="text-sm font-semibold text-[var(--text)] mb-2">{store}</p>
                    <ul className="space-y-1">
                      {storeItems.map((it, i) => (
                        <li key={i} className="text-xs text-[var(--text-secondary)] flex justify-between">
                          <span>{it.name} x{it.quantity}</span>
                          <span>${(it.estimated_price || 0).toFixed(2)}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            <div className="card p-6 gradient-bg text-white">
              <p className="text-sm text-white/80 mb-1">Estimado total</p>
              <p className="text-3xl font-bold">${(data?.estimated_total || 0).toFixed(2)}</p>
              <p className="text-xs text-white/70 mt-2">Basado en precios históricos de tus tickets.</p>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

export default function ShoppingListPage() {
  return (
    <AuthGuard>
      <AppNav />
      <ShoppingListContent />
    </AuthGuard>
  );
}
