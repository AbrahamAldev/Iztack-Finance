/**
 * Página /settings
 * Configuración general del tenant (preferencias, cuenta, integraciones).
 */
"use client";

import { useState } from "react";
import { Save, Printer, User, Globe } from "lucide-react";

export default function SettingsPage() {
  const [tenantName, setTenantName] = useState("Familia Pérez");
  const [currency, setCurrency] = useState("MXN");
  const [timezone, setTimezone] = useState("America/Mexico_City");
  const [printerEnabled, setPrinterEnabled] = useState(false);
  const [savedAt, setSavedAt] = useState<string | null>(null);

  function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSavedAt(new Date().toLocaleString("es-MX"));
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Configuración</h1>
      <p className="text-sm text-gray-500 mb-8">
        Ajustes generales de tu cuenta y del sistema
      </p>

      <div className="max-w-3xl">
        <form onSubmit={handleSave} className="space-y-6">
          {/* Cuenta */}
          <section className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-2 mb-4">
              <User className="h-5 w-5 text-indigo-600" />
              <h2 className="text-lg font-semibold text-gray-900">Cuenta</h2>
            </div>
            <div className="space-y-4">
              <Field label="Nombre del tenant (familia u organización)">
                <input
                  type="text"
                  value={tenantName}
                  onChange={(e) => setTenantName(e.target.value)}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </Field>
              <Field label="Moneda">
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="MXN">MXN — Peso mexicano</option>
                  <option value="USD">USD — Dólar</option>
                  <option value="EUR">EUR — Euro</option>
                </select>
              </Field>
            </div>
          </section>

          {/* Regional */}
          <section className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-2 mb-4">
              <Globe className="h-5 w-5 text-indigo-600" />
              <h2 className="text-lg font-semibold text-gray-900">Regional</h2>
            </div>
            <Field label="Zona horaria">
              <select
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="America/Mexico_City">Ciudad de México (UTC-6)</option>
                <option value="America/Tijuana">Tijuana (UTC-8)</option>
                <option value="America/Monterrey">Monterrey (UTC-6)</option>
                <option value="America/Cancun">Cancún (UTC-5)</option>
              </select>
            </Field>
          </section>

          {/* Hardware */}
          <section className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-2 mb-4">
              <Printer className="h-5 w-5 text-indigo-600" />
              <h2 className="text-lg font-semibold text-gray-900">Hardware</h2>
            </div>
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={printerEnabled}
                onChange={(e) => setPrinterEnabled(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-sm text-gray-700">
                Habilitar impresora de tickets local (USB/Bluetooth)
              </span>
            </label>
            {printerEnabled && (
              <p className="mt-3 text-xs text-gray-500">
                💡 Para configurar el puerto USB o la MAC Bluetooth, edita{" "}
                <code className="bg-gray-100 px-1 rounded">.env</code> y reinicia el contenedor del backend.
              </p>
            )}
          </section>

          {/* Save bar */}
          <div className="flex items-center justify-between bg-white rounded-lg shadow p-4">
            <button
              type="submit"
              className="inline-flex items-center gap-2 bg-indigo-600 px-4 py-2 text-sm font-medium text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              <Save className="h-4 w-4" />
              Guardar cambios
            </button>
            {savedAt && (
              <span className="text-sm text-emerald-600">
                ✓ Guardado a las {savedAt}
              </span>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-gray-700">{label}</span>
      {children}
    </label>
  );
}