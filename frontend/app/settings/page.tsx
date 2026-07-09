"use client";

import { useState, useEffect } from "react";
import { Save, Printer, User, Globe, Send, HardDrive, HelpCircle } from "lucide-react";
import AuthGuard from "../components/AuthGuard";
import AppNav from "../components/AppNav";

function SettingsContent() {
  const [tenantName, setTenantName] = useState("Familia Pérez");
  const [currency, setCurrency] = useState("MXN");
  const [timezone, setTimezone] = useState("America/Mexico_City");
  const [printerEnabled, setPrinterEnabled] = useState(false);
  const [savedAt, setSavedAt] = useState<string | null>(null);

  // Telegram
  const [telegramChatId, setTelegramChatId] = useState("");
  const [telegramConfigured, setTelegramConfigured] = useState(false);
  const [showTelegramHelp, setShowTelegramHelp] = useState(false);

  // Google Drive
  const [driveRefreshToken, setDriveRefreshToken] = useState("");
  const [driveFolderId, setDriveFolderId] = useState("");
  const [driveConfigured, setDriveConfigured] = useState(false);
  const [driveStatus, setDriveStatus] = useState<{ percentage: number; warning: boolean } | null>(null);

  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const t = localStorage.getItem("iztack_token");
    setToken(t);
    if (t) {
      fetchSettings(t);
    }
  }, []);

  async function fetchSettings(t: string) {
    try {
      const res = await fetch("/api/settings", {
        headers: { Authorization: `Bearer ${t}` },
      });
      if (res.ok) {
        const data = await res.json();
        setTelegramConfigured(data.telegram_configured || false);
        setDriveConfigured(data.google_drive_configured || false);
        if (data.google_drive_configured) {
          fetchDriveStatus(t);
        }
      }
    } catch (e) {
      console.error("Error fetching settings:", e);
    }
  }

  async function fetchDriveStatus(t: string) {
    try {
      const res = await fetch("/api/settings/google-drive/status", {
        headers: { Authorization: `Bearer ${t}` },
      });
      if (res.ok) {
        const data = await res.json();
        if (data.configured) {
          setDriveStatus({
            percentage: data.percentage || 0,
            warning: data.warning || false,
          });
        }
      }
    } catch (e) {
      console.error("Error fetching drive status:", e);
    }
  }

  function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSavedAt(new Date().toLocaleString("es-MX"));
  }

  async function saveTelegram() {
    if (!token || !telegramChatId.trim()) return;
    try {
      const res = await fetch("/api/settings/telegram", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ chat_id: telegramChatId.trim() }),
      });
      if (res.ok) {
        setTelegramConfigured(true);
        alert("✅ Chat ID de Telegram guardado");
      } else {
        alert("❌ Error al guardar");
      }
    } catch (e) {
      alert("❌ Error de conexión");
    }
  }

  async function saveDrive() {
    if (!token || !driveRefreshToken.trim() || !driveFolderId.trim()) return;
    try {
      const res = await fetch("/api/settings/google-drive", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          refresh_token: driveRefreshToken.trim(),
          folder_id: driveFolderId.trim(),
        }),
      });
      if (res.ok) {
        setDriveConfigured(true);
        fetchDriveStatus(token);
        alert("✅ Google Drive configurado");
      } else {
        alert("❌ Error al guardar");
      }
    } catch (e) {
      alert("❌ Error de conexión");
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Configuración</h1>
      <p className="text-sm text-gray-500 mb-8">
        Ajustes de tu cuenta, integraciones y almacenamiento
      </p>

      <div className="max-w-3xl space-y-6">
        {/* Telegram */}
        <section className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <Send className="h-5 w-5 text-sky-600" />
            <h2 className="text-lg font-semibold text-gray-900">Telegram</h2>
            {telegramConfigured && (
              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                Configurado
              </span>
            )}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={telegramChatId}
              onChange={(e) => setTelegramChatId(e.target.value)}
              placeholder="Ej: 123456789"
              className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
            />
            <button
              onClick={saveTelegram}
              className="px-4 py-2 bg-sky-600 text-white text-sm rounded-md hover:bg-sky-700"
            >
              Guardar
            </button>
            <button
              onClick={() => setShowTelegramHelp(!showTelegramHelp)}
              className="p-2 text-gray-400 hover:text-gray-600"
              title="Ayuda"
            >
              <HelpCircle className="h-5 w-5" />
            </button>
          </div>
          {showTelegramHelp && (
            <div className="mt-3 p-3 bg-sky-50 rounded-md text-sm text-sky-800">
              <p className="font-semibold mb-1">¿Cómo obtener tu Chat ID?</p>
              <ol className="list-decimal list-inside space-y-1">
                <li>Abre Telegram y busca <code>@userinfobot</code></li>
                <li>Envíale cualquier mensaje (ej: "hola")</li>
                <li>El bot te responderá con tu ID numérico</li>
                <li>Copia ese número y pégalo arriba</li>
              </ol>
            </div>
          )}
        </section>

        {/* Google Drive */}
        <section className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <HardDrive className="h-5 w-5 text-green-600" />
            <h2 className="text-lg font-semibold text-gray-900">Google Drive</h2>
            {driveConfigured && (
              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                Configurado
              </span>
            )}
          </div>

          {driveStatus && (
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span>Almacenamiento usado</span>
                <span>{driveStatus.percentage.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    driveStatus.warning ? "bg-red-500" : "bg-green-500"
                  }`}
                  style={{ width: `${Math.min(driveStatus.percentage, 100)}%` }}
                />
              </div>
              {driveStatus.warning && (
                <p className="text-xs text-red-600 mt-1">
                  ⚠️ Alcanzando límite. Libera espacio o actualiza tu plan.
                </p>
              )}
            </div>
          )}

          <div className="space-y-3">
            <Field label="Refresh Token de Google">
              <input
                type="password"
                value={driveRefreshToken}
                onChange={(e) => setDriveRefreshToken(e.target.value)}
                placeholder="Token de actualización de OAuth"
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
              />
            </Field>
            <Field label="ID de Carpeta de Drive">
              <input
                type="text"
                value={driveFolderId}
                onChange={(e) => setDriveFolderId(e.target.value)}
                placeholder="Ej: 1AbCdEfGhIjKlMnOpQrStUvWxYz"
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
              />
            </Field>
            <button
              onClick={saveDrive}
              className="px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700"
            >
              Guardar Google Drive
            </button>
          </div>
        </section>

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
            type="button"
            onClick={handleSave}
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
      </div>
    </div>
  );
}

export default function SettingsPage() {
  return (
    <AuthGuard>
      <AppNav />
      <SettingsContent />
    </AuthGuard>
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