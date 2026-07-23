/**
 * Página /setup
 * Wizard de configuración inicial del tenant.
 */
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Circle,
  ExternalLink,
  Eye,
  EyeOff,
  HelpCircle,
  Loader2,
  Lock,
  MessageCircle,
  RefreshCw,
  Sparkles,
  XCircle,
} from "lucide-react";

type Provider = "telegram" | "gemini" | "google";
type Status = "idle" | "validating" | "valid" | "invalid";

interface ProviderState {
  value: string;
  status: Status;
  message?: string;
  helpOpen: boolean;
  showSecret: boolean;
}

const PROVIDER_LABELS: Record<Provider, string> = {
  telegram: "Telegram",
  gemini: "Google Gemini",
  google: "Google APIs",
};

const PROVIDER_HINTS: Record<Provider, string> = {
  telegram: "Habla con @BotFather en Telegram, manda /newbot y copia el token que te da.",
  gemini: "Ve a aistudio.google.com → API keys → Create API key. El bot lo usa para OCR y clasificación.",
  google: "Crea un OAuth Client en console.cloud.google.com con scope Gmail + Drive. Pega el refresh token después de autorizar.",
};

const PROVIDER_DOCS: Record<Provider, string> = {
  telegram: "https://core.telegram.org/bots/tutorial#obtain-your-bot-token",
  gemini: "https://aistudio.google.com/app/apikey",
  google: "https://console.cloud.google.com/apis/credentials",
};

const PROVIDER_ORDER: Provider[] = ["telegram", "gemini", "google"];

export default function SetupWizardPage() {
  const router = useRouter();

  const [step, setStep] = useState(0);
  const [tenantName, setTenantName] = useState("Familia Pérez");
  const [providers, setProviders] = useState<Record<Provider, ProviderState>>({
    telegram: { value: "", status: "idle", helpOpen: false, showSecret: false },
    gemini: { value: "", status: "idle", helpOpen: false, showSecret: false },
    google: { value: "", status: "idle", helpOpen: false, showSecret: false },
  });
  const [finalizing, setFinalizing] = useState(false);
  const [finalError, setFinalError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const saved = localStorage.getItem("iztack_theme");
    if (saved === "dark" || (!saved && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
      document.documentElement.classList.add("dark");
    }
    fetch("/api/setup/status")
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data?.completed) router.replace("/dashboard");
      })
      .catch(() => {});
  }, [router]);

  function setProviderField(p: Provider, patch: Partial<ProviderState>) {
    setProviders((prev) => ({ ...prev, [p]: { ...prev[p], ...patch } }));
  }

  async function validateProvider(p: Provider) {
    const current = providers[p];
    if (!current.value.trim()) {
      setProviderField(p, { status: "invalid", message: "El valor no puede estar vacío." });
      return;
    }
    setProviderField(p, { status: "validating", message: undefined });
    try {
      const res = await fetch("/api/setup/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider: p, value: current.value }),
      });
      const data = await res.json();
      if (res.ok && data.valid) {
        setProviderField(p, { status: "valid", message: data.message || "Conexión exitosa" });
      } else {
        setProviderField(p, { status: "invalid", message: data.detail || data.message || "La credencial no es válida." });
      }
    } catch (err: unknown) {
      setProviderField(p, {
        status: "invalid",
        message: `No se pudo conectar al backend: ${err instanceof Error ? err.message : "error desconocido"}`,
      });
    }
  }

  async function finalize() {
    setFinalError(null);
    setFinalizing(true);
    try {
      const res = await fetch("/api/setup/finalize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tenant_name: tenantName,
          telegram_bot_token: providers.telegram.value,
          gemini_api_key: providers.gemini.value,
          google_client_id: providers.google.value,
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.detail || "No se pudo finalizar el setup.");
      }
      router.push("/dashboard?welcome=1");
    } catch (err: unknown) {
      setFinalError(err instanceof Error ? err.message : "Error desconocido al finalizar.");
      setFinalizing(false);
    }
  }

  const currentProvider = PROVIDER_ORDER[step];
  const allValid = PROVIDER_ORDER.every((p) => providers[p].status === "valid");
  const isLastStep = step === PROVIDER_ORDER.length;

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-indigo-50 dark:from-surface-900 dark:via-surface-900 dark:to-surface-800 -z-20" />
      <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-primary-400/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4 -z-10" />

      <header className="border-b border-[var(--border)] glass">
        <div className="max-w-3xl mx-auto px-4 py-5 sm:px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center text-white shadow-glow">
              <Lock className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-[var(--text)]">Configuración Inicial</h1>
              <p className="text-xs text-[var(--text-muted)]">Solo te tomará 2 minutos.</p>
            </div>
          </div>
          <span className="hidden sm:inline-flex items-center gap-1 px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 text-xs font-semibold">
            <Lock className="h-3 w-3" /> cifrado en reposo
          </span>
        </div>
      </header>

      <main className={`max-w-3xl mx-auto px-4 py-10 sm:px-6 transition-all duration-700 ${mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}`}>
        <ol className="mb-10 flex items-center justify-between">
          {PROVIDER_ORDER.map((p, idx) => {
            const isDone = providers[p].status === "valid";
            const isCurrent = idx === step;
            const isComplete = idx < PROVIDER_ORDER.length ? isDone : allValid;
            return (
              <li key={p} className="flex-1 flex items-center">
                <button onClick={() => setStep(idx)} className="flex flex-col items-center" type="button">
                  <span
                    className={`flex items-center justify-center h-10 w-10 rounded-full border-2 text-sm font-bold transition-all ${
                      isComplete
                        ? "bg-emerald-500 border-emerald-500 text-white"
                        : isCurrent
                        ? "border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400"
                        : "border-[var(--border)] text-[var(--text-muted)]"
                    }`}
                  >
                    {isComplete ? <CheckCircle2 className="h-5 w-5" /> : <span>{idx + 1}</span>}
                  </span>
                  <span className="mt-2 text-[10px] sm:text-xs font-medium text-[var(--text-secondary)] hidden sm:block">{PROVIDER_LABELS[p]}</span>
                </button>
                {idx < PROVIDER_ORDER.length - 1 && (
                  <span
                    className={`flex-1 h-0.5 mx-2 rounded-full ${
                      providers[PROVIDER_ORDER[idx + 1]].status === "valid" || (isDone && idx < step)
                        ? "bg-emerald-500"
                        : "bg-[var(--border)]"
                    }`}
                  />
                )}
              </li>
            );
          })}
        </ol>

        {!isLastStep ? (
          <ProviderStep
            provider={currentProvider}
            state={providers[currentProvider]}
            tenantName={tenantName}
            onTenantNameChange={setTenantName}
            onChange={(v) => setProviderField(currentProvider, { value: v, status: "idle" })}
            onToggleHelp={() => setProviderField(currentProvider, { helpOpen: !providers[currentProvider].helpOpen })}
            onToggleSecret={() => setProviderField(currentProvider, { showSecret: !providers[currentProvider].showSecret })}
            onValidate={() => validateProvider(currentProvider)}
            onNext={() => setStep(step + 1)}
          />
        ) : (
          <FinalStep
            tenantName={tenantName}
            allValid={allValid}
            finalizing={finalizing}
            finalError={finalError}
            onBack={() => setStep(PROVIDER_ORDER.length - 1)}
            onConfirm={finalize}
          />
        )}
      </main>
    </div>
  );
}

interface ProviderStepProps {
  provider: Provider;
  state: ProviderState;
  tenantName: string;
  onTenantNameChange: (v: string) => void;
  onChange: (v: string) => void;
  onToggleHelp: () => void;
  onToggleSecret: () => void;
  onValidate: () => void;
  onNext: () => void;
}

function ProviderStep({
  provider,
  state,
  tenantName,
  onTenantNameChange,
  onChange,
  onToggleHelp,
  onToggleSecret,
  onValidate,
  onNext,
}: ProviderStepProps) {
  const isSecret = provider !== "telegram";
  const Icon = provider === "telegram" ? MessageCircle : provider === "gemini" ? Sparkles : RefreshCw;

  return (
    <section className="card p-6 sm:p-8">
      <div className="flex items-center gap-4 mb-6">
        <div className="w-12 h-12 rounded-xl bg-primary-50 dark:bg-primary-500/10 flex items-center justify-center text-primary-600 dark:text-primary-400">
          <Icon className="h-6 w-6" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-[var(--text)]">{PROVIDER_LABELS[provider]}</h2>
          <p className="text-sm text-[var(--text-muted)]">
            {provider === "telegram"
              ? "Necesario para enviar y recibir tickets."
              : provider === "gemini"
              ? "Necesario para entender tickets y conversar contigo."
              : "Necesario para guardar facturas y revisar tu correo."}
          </p>
        </div>
      </div>

      {provider === "telegram" && (
        <div className="mb-5">
          <label className="block text-sm font-semibold mb-2 text-[var(--text)]">Nombre del tenant (familia u organización)</label>
          <input
            type="text"
            value={tenantName}
            onChange={(e) => onTenantNameChange(e.target.value)}
            className="input"
            placeholder="Familia Pérez"
          />
        </div>
      )}

      <div className="mb-5">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-semibold text-[var(--text)]">
            {provider === "telegram" ? "Bot Token" : provider === "gemini" ? "API Key" : "Client ID / Refresh Token"}
          </label>
          <button type="button" onClick={onToggleHelp} className="inline-flex items-center gap-1 text-xs font-medium text-primary-600 dark:text-primary-400 hover:underline">
            <HelpCircle className="h-3 w-3" /> ¿Cómo consigo esto?
          </button>
        </div>
        <div className="relative">
          <input
            type={isSecret && !state.showSecret ? "password" : "text"}
            value={state.value}
            onChange={(e) => onChange(e.target.value)}
            className="input pr-10 font-mono text-sm"
            placeholder={
              provider === "telegram" ? "123456789:ABCdefGHIjklMNOpqrsTUVwxyz" : provider === "gemini" ? "AIzaSy..." : "ya29.a0..."
            }
            autoComplete="off"
            spellCheck={false}
          />
          {isSecret && (
            <button
              type="button"
              onClick={onToggleSecret}
              className="absolute inset-y-0 right-0 px-3 flex items-center text-[var(--text-muted)] hover:text-[var(--text)]"
              aria-label={state.showSecret ? "Ocultar" : "Mostrar"}
            >
              {state.showSecret ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          )}
        </div>

        {state.helpOpen && (
          <div className="mt-3 rounded-xl bg-primary-50 dark:bg-primary-500/10 border border-primary-100 dark:border-primary-500/20 p-4 text-sm">
            <p className="text-[var(--text-secondary)]">{PROVIDER_HINTS[provider]}</p>
            <a
              href={PROVIDER_DOCS[provider]}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-3 inline-flex items-center gap-1 font-semibold text-primary-700 dark:text-primary-300 hover:underline"
            >
              Ver guía completa <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        )}
      </div>

      <div className="min-h-[2.5rem] mb-6">
        {state.status === "validating" && (
          <p className="inline-flex items-center gap-2 text-sm text-[var(--text-muted)]">
            <Loader2 className="h-4 w-4 animate-spin" /> Validando con el servidor…
          </p>
        )}
        {state.status === "valid" && (
          <p className="inline-flex items-center gap-2 text-sm text-emerald-700 dark:text-emerald-400 font-medium">
            <CheckCircle2 className="h-4 w-4" /> {state.message}
          </p>
        )}
        {state.status === "invalid" && (
          <p className="inline-flex items-center gap-2 text-sm text-red-700 dark:text-red-400 font-medium">
            <XCircle className="h-4 w-4" /> {state.message}
          </p>
        )}
        {state.status === "idle" && (
          <p className="text-xs text-[var(--text-muted)]">Cuando termines, pulsa "Validar" para confirmar que funciona.</p>
        )}
      </div>

      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={onValidate}
          disabled={state.status === "validating" || !state.value.trim()}
          className="btn btn-secondary"
        >
          {state.status === "validating" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Circle className="h-4 w-4" />}
          Validar
        </button>
        <button
          type="button"
          onClick={onNext}
          disabled={state.status !== "valid"}
          className="btn btn-primary"
        >
          Siguiente <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </section>
  );
}

interface FinalStepProps {
  tenantName: string;
  allValid: boolean;
  finalizing: boolean;
  finalError: string | null;
  onBack: () => void;
  onConfirm: () => void;
}

function FinalStep({ tenantName, allValid, finalizing, finalError, onBack, onConfirm }: FinalStepProps) {
  return (
    <section className="card p-6 sm:p-8">
      <h2 className="text-xl font-bold text-[var(--text)]">Confirmar y empezar</h2>
      <p className="text-sm text-[var(--text-muted)] mt-1">
        Revisa que todo esté en orden. Al confirmar, las credenciales se guardarán y el bot se reiniciará.
      </p>

      <ul className="mt-6 divide-y divide-[var(--border)] border border-[var(--border)] rounded-xl overflow-hidden">
        <li className="flex items-center justify-between p-4 bg-[var(--surface-elevated)]">
          <span className="text-sm font-semibold text-[var(--text)]">Tenant</span>
          <span className="text-sm text-[var(--text-secondary)]">{tenantName}</span>
        </li>
        {PROVIDER_ORDER.map((p) => (
          <li key={p} className="flex items-center justify-between p-4">
            <span className="text-sm font-semibold text-[var(--text)]">{PROVIDER_LABELS[p]}</span>
            <span className="inline-flex items-center gap-2 text-sm text-emerald-700 dark:text-emerald-400 font-medium">
              <CheckCircle2 className="h-4 w-4" /> Validado
            </span>
          </li>
        ))}
      </ul>

      {finalError && (
        <p className="mt-4 inline-flex items-start gap-2 text-sm text-red-700 dark:text-red-400">
          <XCircle className="h-4 w-4 mt-0.5" /> {finalError}
        </p>
      )}

      <div className="mt-6 flex items-center justify-between">
        <button type="button" onClick={onBack} disabled={finalizing} className="btn btn-secondary">
          <ArrowLeft className="h-4 w-4" /> Atrás
        </button>
        <button
          type="button"
          onClick={onConfirm}
          disabled={!allValid || finalizing}
          className="btn btn-primary bg-emerald-600 hover:bg-emerald-700"
        >
          {finalizing ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
          Guardar y arrancar
        </button>
      </div>
    </section>
  );
}
