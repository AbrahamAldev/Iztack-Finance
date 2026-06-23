/**
 * Página /setup
 * Wizard de configuración inicial del tenant.
 *
 * El usuario introduce sus credenciales de Telegram, Gemini y Google paso a paso.
 * En cada paso, el backend valida la credencial en vivo (sin guardarla todavía).
 * Al confirmar todo, el backend escribe las credenciales en el `.env` del contenedor
 * y reinicia el bot.
 *
 * Si el wizard ya se completó antes, el componente redirige al /dashboard.
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
  google: "Google APIs (Gmail + Drive)",
};

const PROVIDER_HINTS: Record<Provider, string> = {
  telegram:
    "Habla con @BotFather en Telegram, manda /newbot y copia el token que te da.",
  gemini:
    "Ve a aistudio.google.com → API keys → Create API key. El bot lo usa para OCR y clasificación.",
  google:
    "Crea un OAuth Client en console.cloud.google.com con scope Gmail + Drive. Pega el refresh token después de autorizar.",
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

  // Al montar, pregunta al backend si ya está configurado
  useEffect(() => {
    fetch("/api/setup/status")
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data?.completed) {
          router.replace("/dashboard");
        }
      })
      .catch(() => {
        /* si falla, dejamos al usuario pasar */
      });
  }, [router]);

  function setProviderField(p: Provider, patch: Partial<ProviderState>) {
    setProviders((prev) => ({ ...prev, [p]: { ...prev[p], ...patch } }));
  }

  async function validateProvider(p: Provider) {
    const current = providers[p];
    if (!current.value.trim()) {
      setProviderField(p, {
        status: "invalid",
        message: "El valor no puede estar vacío.",
      });
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
        setProviderField(p, {
          status: "valid",
          message: data.message || "Conexión exitosa",
        });
      } else {
        setProviderField(p, {
          status: "invalid",
          message: data.detail || data.message || "La credencial no es válida.",
        });
      }
    } catch (err: unknown) {
      setProviderField(p, {
        status: "invalid",
        message: `No se pudo conectar al backend: ${
          err instanceof Error ? err.message : "error desconocido"
        }`,
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
          google_client_id: providers.google.value, // o refresh_token, según flujo
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.detail || "No se pudo finalizar el setup.");
      }
      router.push("/dashboard?welcome=1");
    } catch (err: unknown) {
      setFinalError(
        err instanceof Error ? err.message : "Error desconocido al finalizar."
      );
      setFinalizing(false);
    }
  }

  const currentProvider = PROVIDER_ORDER[step];
  const allValid = PROVIDER_ORDER.every(
    (p) => providers[p].status === "valid"
  );
  const isLastStep = step === PROVIDER_ORDER.length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="max-w-3xl mx-auto px-4 py-5 sm:px-6 lg:px-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Configuración Inicial
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Solo te tomará 2 minutos. Las credenciales se guardan de forma segura.
            </p>
          </div>
          <span className="hidden sm:inline-flex items-center gap-1 px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-medium">
            <Lock className="h-3 w-3" />
            cifrado en reposo
          </span>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-10 sm:px-6 lg:px-8">
        {/* Stepper */}
        <ol className="mb-10 flex items-center justify-between">
          {PROVIDER_ORDER.map((p, idx) => {
            const isDone = providers[p].status === "valid";
            const isCurrent = idx === step;
            const isComplete = idx < PROVIDER_ORDER.length ? isDone : allValid;
            return (
              <li key={p} className="flex-1 flex items-center">
                <button
                  onClick={() => setStep(idx)}
                  className="flex flex-col items-center"
                  type="button"
                >
                  <span
                    className={`flex items-center justify-center h-9 w-9 rounded-full border-2 ${
                      isComplete
                        ? "bg-emerald-500 border-emerald-500 text-white"
                        : isCurrent
                        ? "border-indigo-600 text-indigo-600"
                        : "border-gray-300 text-gray-400"
                    }`}
                  >
                    {isComplete ? (
                      <CheckCircle2 className="h-5 w-5" />
                    ) : (
                      <span className="text-sm font-semibold">{idx + 1}</span>
                    )}
                  </span>
                  <span className="mt-2 text-xs font-medium text-gray-700">
                    {PROVIDER_LABELS[p]}
                  </span>
                </button>
                {idx < PROVIDER_ORDER.length - 1 && (
                  <span
                    className={`flex-1 h-0.5 mx-2 ${
                      providers[PROVIDER_ORDER[idx + 1]].status === "valid" ||
                      (isDone && idx < step)
                        ? "bg-emerald-500"
                        : "bg-gray-200"
                    }`}
                  />
                )}
              </li>
            );
          })}
        </ol>

        {/* Step content */}
        {!isLastStep ? (
          <ProviderStep
            provider={currentProvider}
            state={providers[currentProvider]}
            tenantName={tenantName}
            onTenantNameChange={setTenantName}
            onChange={(v) =>
              setProviderField(currentProvider, { value: v, status: "idle" })
            }
            onToggleHelp={() =>
              setProviderField(currentProvider, {
                helpOpen: !providers[currentProvider].helpOpen,
              })
            }
            onToggleSecret={() =>
              setProviderField(currentProvider, {
                showSecret: !providers[currentProvider].showSecret,
              })
            }
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
  const isSecret = provider !== "telegram"; // tokens y API keys son sensibles
  const Icon =
    provider === "telegram" ? MessageCircle : provider === "gemini" ? Sparkles : RefreshCw;

  return (
    <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sm:p-8">
      <div className="flex items-center gap-3 mb-2">
        <span className="flex items-center justify-center h-10 w-10 rounded-lg bg-indigo-100 text-indigo-600">
          <Icon className="h-5 w-5" />
        </span>
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            {PROVIDER_LABELS[provider]}
          </h2>
          <p className="text-sm text-gray-500">
            {provider === "telegram"
              ? "Necesario para enviar y recibir tickets."
              : provider === "gemini"
              ? "Necesario para entender tickets y conversar contigo."
              : "Necesario para guardar facturas y revisar tu correo."}
          </p>
        </div>
      </div>

      {provider === "telegram" && (
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nombre del tenant (familia u organización)
          </label>
          <input
            type="text"
            value={tenantName}
            onChange={(e) => onTenantNameChange(e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            placeholder="Familia Pérez"
          />
        </div>
      )}

      <div className="mt-4">
        <div className="flex items-center justify-between mb-1">
          <label className="block text-sm font-medium text-gray-700">
            {provider === "telegram"
              ? "Bot Token"
              : provider === "gemini"
              ? "API Key"
              : "Client ID / Refresh Token"}
          </label>
          <button
            type="button"
            onClick={onToggleHelp}
            className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-700"
          >
            <HelpCircle className="h-3 w-3" />
            ¿Cómo consigo esto?
          </button>
        </div>
        <div className="relative">
          <input
            type={isSecret && !state.showSecret ? "password" : "text"}
            value={state.value}
            onChange={(e) => onChange(e.target.value)}
            className="w-full rounded-md border border-gray-300 pl-3 pr-10 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
            placeholder={
              provider === "telegram"
                ? "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                : provider === "gemini"
                ? "AIzaSy..."
                : "ya29.a0..."
            }
            autoComplete="off"
            spellCheck={false}
          />
          {isSecret && (
            <button
              type="button"
              onClick={onToggleSecret}
              className="absolute inset-y-0 right-0 px-3 flex items-center text-gray-400 hover:text-gray-600"
              aria-label={state.showSecret ? "Ocultar" : "Mostrar"}
            >
              {state.showSecret ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          )}
        </div>

        {state.helpOpen && (
          <div className="mt-2 rounded-md bg-blue-50 border border-blue-200 p-3 text-xs text-blue-900">
            <p>{PROVIDER_HINTS[provider]}</p>
            <a
              href={PROVIDER_DOCS[provider]}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-2 inline-flex items-center gap-1 font-medium text-blue-700 hover:underline"
            >
              Ver guía completa
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        )}
      </div>

      {/* Status */}
      <div className="mt-4 min-h-[2.25rem]">
        {state.status === "validating" && (
          <p className="inline-flex items-center gap-2 text-sm text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin" />
            Validando con el servidor…
          </p>
        )}
        {state.status === "valid" && (
          <p className="inline-flex items-center gap-2 text-sm text-emerald-700">
            <CheckCircle2 className="h-4 w-4" />
            {state.message}
          </p>
        )}
        {state.status === "invalid" && (
          <p className="inline-flex items-center gap-2 text-sm text-rose-700">
            <XCircle className="h-4 w-4" />
            {state.message}
          </p>
        )}
        {state.status === "idle" && (
          <p className="text-xs text-gray-400">
            Cuando termines, pulsa "Validar" para confirmar que funciona.
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="mt-6 flex items-center justify-between">
        <button
          type="button"
          onClick={onValidate}
          disabled={state.status === "validating" || !state.value.trim()}
          className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
        >
          {state.status === "validating" ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Circle className="h-4 w-4" />
          )}
          Validar
        </button>
        <button
          type="button"
          onClick={onNext}
          disabled={state.status !== "valid"}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
        >
          Siguiente
          <ArrowRight className="h-4 w-4" />
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

function FinalStep({
  tenantName,
  allValid,
  finalizing,
  finalError,
  onBack,
  onConfirm,
}: FinalStepProps) {
  return (
    <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sm:p-8">
      <h2 className="text-lg font-semibold text-gray-900">Confirmar y empezar</h2>
      <p className="mt-1 text-sm text-gray-500">
        Revisa que todo esté en orden. Al confirmar, las credenciales se guardarán
        y el bot se reiniciará (tarda unos segundos).
      </p>

      <ul className="mt-6 divide-y divide-gray-200 border border-gray-200 rounded-md">
        <li className="flex items-center justify-between p-4">
          <span className="text-sm font-medium text-gray-700">Tenant</span>
          <span className="text-sm text-gray-900">{tenantName}</span>
        </li>
        {PROVIDER_ORDER.map((p) => (
          <li key={p} className="flex items-center justify-between p-4">
            <span className="text-sm font-medium text-gray-700">
              {PROVIDER_LABELS[p]}
            </span>
            <span className="inline-flex items-center gap-2 text-sm text-emerald-700">
              <CheckCircle2 className="h-4 w-4" />
              Validado
            </span>
          </li>
        ))}
      </ul>

      {finalError && (
        <p className="mt-4 inline-flex items-start gap-2 text-sm text-rose-700">
          <XCircle className="h-4 w-4 mt-0.5" />
          {finalError}
        </p>
      )}

      <div className="mt-6 flex items-center justify-between">
        <button
          type="button"
          onClick={onBack}
          disabled={finalizing}
          className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
        >
          <ArrowLeft className="h-4 w-4" />
          Atrás
        </button>
        <button
          type="button"
          onClick={onConfirm}
          disabled={!allValid || finalizing}
          className="inline-flex items-center gap-2 px-5 py-2 rounded-md text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50"
        >
          {finalizing ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <CheckCircle2 className="h-4 w-4" />
          )}
          Guardar y arrancar el bot
        </button>
      </div>
    </section>
  );
}