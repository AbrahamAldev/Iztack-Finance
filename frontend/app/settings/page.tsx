"use client";

import { useState, useEffect } from "react";
import { Save, Printer, User, Globe, Send, HardDrive, HelpCircle, CheckCircle2, Shield, Moon, Sun, Monitor } from "lucide-react";
import AuthGuard from "../components/AuthGuard";
import AppNav from "../components/AppNav";

function SettingsContent() {
  const [tenantName, setTenantName] = useState("Familia Pérez");
  const [currency, setCurrency] = useState("MXN");
  const [timezone, setTimezone] = useState("America/Mexico_City");
  const [printerEnabled, setPrinterEnabled] = useState(false);
  const [savedAt, setSavedAt] = useState<string | null>(null);
  const [themeMode, setThemeMode] = useState<"auto" | "light" | "dark">("auto");

  const [telegramChatId, setTelegramChatId] = useState("");
  const [telegramConfigured, setTelegramConfigured] = useState(false);
  const [showTelegramHelp, setShowTelegramHelp] = useState(false);

  const [driveRefreshToken, setDriveRefreshToken] = useState("");
  const [driveFolderId, setDriveFolderId] = useState("");
  const [driveConfigured, setDriveConfigured] = useState(false);
  const [showDriveHelp, setShowDriveHelp] = useState(false);
  const [driveStatus, setDriveStatus] = useState<{ percentage: number; warning: boolean } | null>(null);

  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const t = localStorage.getItem("iztack_token");
    const savedTheme = localStorage.getItem("iztack_theme") as "auto" | "light" | "dark" | null;
    setThemeMode(savedTheme || "auto");
    setToken(t);
    if (t) fetchSettings(t);
  }, []);

  async function fetchSettings(t: string) {
    try {
      const res = await fetch("/api/settings", { headers: { Authorization: `Bearer ${t}` } });
      if (res.ok) {
        const data = await res.json();
        setTelegramConfigured(data.telegram_configured || false);
        setDriveConfigured(data.google_drive_configured || false);
        if (data.google_drive_configured) fetchDriveStatus(t);
      }
    } catch (e) {
      console.error("Error fetching settings:", e);
    }
  }

  async function fetchDriveStatus(t: string) {
    try {
      const res = await fetch("/api/settings/google-drive/status", { headers: { Authorization: `Bearer ${t}` } });
      if (res.ok) {
        const data = await res.json();
        if (data.configured) setDriveStatus({ percentage: data.percentage || 0, warning: data.warning || false });
      }
    } catch (e) {
      console.error("Error fetching drive status:", e);
    }
  }

  function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSavedAt(new Date().toLocaleString("es-MX"));
  }

  function applyTheme(mode: "auto" | "light" | "dark") {
    setThemeMode(mode);
    localStorage.setItem("iztack_theme", mode);
    const isDark = mode === "dark" || (mode === "auto" && window.matchMedia("(prefers-color-scheme: dark)").matches);
    document.documentElement.classList.toggle("dark", isDark);
  }

  async function saveTelegram() {
    if (!token || !telegramChatId.trim()) return;
    try {
      const res = await fetch("/api/settings/telegram", {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ chat_id: telegramChatId.trim() }),
      });
      if (res.ok) {
        setTelegramConfigured(true);
        setSavedAt("Telegram guardado");
      } else if (res.status === 401) {
        localStorage.removeItem("iztack_token");
        window.location.href = "/login";
      }
    } catch (e) {
      console.error(e);
    }
  }

  async function saveDrive() {
    if (!token || !driveRefreshToken.trim() || !driveFolderId.trim()) return;
    try {
      const res = await fetch("/api/settings/google-drive", {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ refresh_token: driveRefreshToken.trim(), folder_id: driveFolderId.trim() }),
      });
      if (res.ok) {
        setDriveConfigured(true);
        fetchDriveStatus(token);
        setSavedAt("Google Drive guardado");
      }
    } catch (e) {
      console.error(e);
    }
  }

  return (
    <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8 animate-slide-up">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[var(--text)]">Configuración</h1>
        <p className="text-[var(--text-secondary)] text-sm mt-1">Personaliza tu cuenta, integraciones y preferencias.</p>
      </div>

      <div className="space-y-6">
        {/* Theme */}
        <section className="card p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
              <Moon className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-[var(--text)]">Apariencia</h2>
              <p className="text-sm text-[var(--text-muted)]">Elige el tema de la interfaz</p>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {[
              { value: "light", label: "Claro", icon: Sun },
              { value: "dark", label: "Oscuro", icon: Moon },
              { value: "auto", label: "Auto", icon: Monitor },
            ].map((opt) => {
              const Icon = opt.icon;
              const active = themeMode === (opt.value as any);
              return (
                <button
                  key={opt.value}
                  onClick={() => applyTheme(opt.value as any)}
                  className={`flex flex-col items-center gap-2 p-4 rounded-xl border transition-all ${
                    active
                      ? "border-primary-500 bg-primary-50 dark:bg-primary-500/10 text-primary-700 dark:text-primary-300"
                      : "border-[var(--border)] bg-[var(--surface-elevated)] text-[var(--text-secondary)] hover:border-primary-300"
                  }`}
                >
                  <Icon className="h-6 w-6" />
                  <span className="text-sm font-medium">{opt.label}</span>
                </button>
              );
            })}
          </div>
        </section>

        {/* Telegram */}
        <section className="card p-6">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-sky-50 dark:bg-sky-500/10 flex items-center justify-center text-sky-600 dark:text-sky-400">
                <Send className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-[var(--text)]">Telegram</h2>
                <p className="text-sm text-[var(--text-muted)]">Recibe notificaciones en tu celular</p>
              </div>
            </div>
            {telegramConfigured && <span className="badge badge-success flex items-center gap-1"><CheckCircle2 className="h-3 w-3" /> Configurado</span>}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={telegramChatId}
              onChange={(e) => setTelegramChatId(e.target.value)}
              placeholder="Ej: 123456789"
              className="input flex-1"
            />
            <button onClick={saveTelegram} className="btn btn-primary whitespace-nowrap">Guardar</button>
            <button onClick={() => setShowTelegramHelp(!showTelegramHelp)} className="p-2.5 text-[var(--text-muted)] hover:bg-[var(--surface-elevated)] rounded-xl" title="Ayuda">
              <HelpCircle className="h-5 w-5" />
            </button>
          </div>
          {showTelegramHelp && (
            <div className="mt-4 bg-sky-50 dark:bg-sky-500/10 border border-sky-100 dark:border-sky-500/20 rounded-xl p-4 text-sm text-sky-800 dark:text-sky-200">
              <p className="font-semibold mb-2">¿Cómo vincular Telegram?</p>
              <ol className="list-decimal list-inside space-y-1 text-[var(--text-secondary)]">
                <li>Busca <strong>@IztackFinance_Bot</strong> en Telegram</li>
                <li>Envía <code>/start</code></li>
                <li>Copia tu <strong>Chat ID</strong> y pégalo aquí</li>
                <li>Haz clic en <strong>Guardar</strong></li>
              </ol>
            </div>
          )}
        </section>

        {/* Google Drive */}
        <section className="card p-6">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                <HardDrive className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-[var(--text)]">Google Drive</h2>
                <p className="text-sm text-[var(--text-muted)]">Respalda facturas y documentos</p>
              </div>
            </div>
            {driveConfigured && <span className="badge badge-success flex items-center gap-1"><CheckCircle2 className="h-3 w-3" /> Configurado</span>}
          </div>

          {driveStatus && (
            <div className="mb-5">
              <div className="flex justify-between text-sm mb-1.5">
                <span className="text-[var(--text-secondary)]">Almacenamiento usado</span>
                <span className="font-semibold text-[var(--text)]">{driveStatus.percentage.toFixed(1)}%</span>
              </div>
              <div className="h-2.5 w-full bg-[var(--surface-elevated)] rounded-full overflow-hidden border border-[var(--border)]">
                <div className={`h-full rounded-full ${driveStatus.warning ? "bg-red-500" : "bg-emerald-500"}`} style={{ width: `${Math.min(driveStatus.percentage, 100)}%` }} />
              </div>
              {driveStatus.warning && <p className="text-xs text-red-500 mt-1">⚠️ Alcanzando límite de espacio.</p>}
            </div>
          )}

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-[var(--text-muted)]">Configura tu almacenamiento en la nube</p>
              <button onClick={() => setShowDriveHelp(!showDriveHelp)} className="p-1.5 text-[var(--text-muted)] hover:bg-[var(--surface-elevated)] rounded-lg">
                <HelpCircle className="h-4 w-4" />
              </button>
            </div>
            {showDriveHelp && (
              <div className="bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-100 dark:border-emerald-500/20 rounded-xl p-4 text-sm">
                <p className="font-semibold mb-2 text-emerald-800 dark:text-emerald-200">¿Cómo obtener credenciales?</p>
                <ol className="list-decimal list-inside space-y-1 text-[var(--text-secondary)]">
                  <li>Ve a <a href="https://console.cloud.google.com/apis/credentials" target="_blank" rel="noopener noreferrer" className="text-emerald-700 dark:text-emerald-400 underline font-medium">Google Cloud Console</a></li>
                  <li>Habilita <strong>Google Drive API</strong></li>
                  <li>Crea credenciales OAuth para app de escritorio</li>
                  <li>Genera un <strong>Refresh Token</strong></li>
                  <li>Crea una carpeta en Drive y copia su ID</li>
                </ol>
                <p className="mt-2 text-xs text-[var(--text-muted)] flex items-center gap-1"><Shield className="h-3 w-3" /> Tus credenciales se cifran con AES-256-GCM</p>
              </div>
            )}
            <Field label="Refresh Token">
              <input type="password" value={driveRefreshToken} onChange={(e) => setDriveRefreshToken(e.target.value)} placeholder="Token de actualización de OAuth" className="input" />
            </Field>
            <Field label="ID de Carpeta">
              <input type="text" value={driveFolderId} onChange={(e) => setDriveFolderId(e.target.value)} placeholder="Ej: 1AbCdEfGhIjKlMnOpQrStUvWxYz" className="input" />
            </Field>
            <button onClick={saveDrive} className="btn btn-primary bg-emerald-600 hover:bg-emerald-700">Guardar Google Drive</button>
          </div>
        </section>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Account */}
          <section className="card p-6">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                <User className="h-5 w-5" />
              </div>
              <h2 className="text-lg font-bold text-[var(--text)]">Cuenta</h2>
            </div>
            <div className="space-y-4">
              <Field label="Nombre del tenant">
                <input type="text" value={tenantName} onChange={(e) => setTenantName(e.target.value)} className="input" />
              </Field>
              <Field label="Moneda">
                <select value={currency} onChange={(e) => setCurrency(e.target.value)} className="input">
                  <option value="MXN">MXN — Peso mexicano</option>
                  <option value="USD">USD — Dólar</option>
                  <option value="EUR">EUR — Euro</option>
                </select>
              </Field>
            </div>
          </section>

          {/* Regional */}
          <section className="card p-6">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                <Globe className="h-5 w-5" />
              </div>
              <h2 className="text-lg font-bold text-[var(--text)]">Regional</h2>
            </div>
            <Field label="Zona horaria">
              <select value={timezone} onChange={(e) => setTimezone(e.target.value)} className="input">
                <option value="America/Mexico_City">Ciudad de México (UTC-6)</option>
                <option value="America/Tijuana">Tijuana (UTC-8)</option>
                <option value="America/Monterrey">Monterrey (UTC-6)</option>
                <option value="America/Cancun">Cancún (UTC-5)</option>
              </select>
            </Field>
          </section>
        </div>

        {/* Hardware */}
        <section className="card p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
              <Printer className="h-5 w-5" />
            </div>
            <h2 className="text-lg font-bold text-[var(--text)]">Hardware</h2>
          </div>
          <label className="flex items-center gap-3 cursor-pointer">
            <input type="checkbox" checked={printerEnabled} onChange={(e) => setPrinterEnabled(e.target.checked)} className="h-5 w-5 rounded border-[var(--border)] text-primary-600 focus:ring-primary-500" />
            <span className="text-sm text-[var(--text-secondary)]">Habilitar impresora de tickets local (USB/Bluetooth)</span>
          </label>
          {printerEnabled && (
            <p className="mt-3 text-xs text-[var(--text-muted)]">💡 Configura el puerto USB o MAC Bluetooth en el archivo <code className="bg-[var(--surface-elevated)] px-1.5 py-0.5 rounded">.env</code></p>
          )}
        </section>

        {/* Save bar */}
        <div className="card p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <button type="button" onClick={handleSave} className="btn btn-primary w-full sm:w-auto">
            <Save className="h-4 w-4" /> Guardar cambios
          </button>
          {savedAt && <span className="text-sm text-emerald-600 dark:text-emerald-400 font-medium">✓ {savedAt}</span>}
        </div>
      </div>
    </main>
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

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-semibold text-[var(--text)]">{label}</span>
      {children}
    </label>
  );
}
