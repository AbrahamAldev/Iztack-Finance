"use client";

import { useState, useEffect } from "react";
import AuthGuard from "../components/AuthGuard";
import AppNav from "../components/AppNav";
import {
  HardDrive,
  Image,
  FileText,
  File,
  Download,
  Trash2,
  ChevronLeft,
  FolderOpen,
  AlertCircle,
  Database,
  Loader2,
  FileX,
  RefreshCw,
} from "lucide-react";
import Link from "next/link";

type TabType = "all" | "tickets" | "invoices";
type FileEntry = {
  id: string;
  type: "ticket" | "invoice";
  has_processed?: boolean;
  has_pdf?: boolean;
  has_xml?: boolean;
  original_size?: number;
  processed_size?: number;
  pdf_size?: number;
  xml_size?: number;
  created_at: string;
};

function formatBytes(bytes?: number) {
  if (!bytes) return "0 B";
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), 3);
  return (bytes / Math.pow(1024, i)).toFixed(1) + " " + sizes[i];
}

function formatDate(iso?: string) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("es-MX", {
    year: "numeric", month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

function StorageContent() {
  const [tab, setTab] = useState<TabType>("all");
  const [files, setFiles] = useState<FileEntry[]>([]);
  const [usage, setUsage] = useState<{ used_bytes: number; max_bytes: number; used_pct: number; free_bytes: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<string | null>(null);

  const token = typeof window !== "undefined" ? localStorage.getItem("iztack_token") : null;

  async function fetchData() {
    if (!token) return;
    setLoading(true);
    try {
      const [usageRes, filesRes] = await Promise.all([
        fetch("/api/storage/usage", { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`/api/storage/files${tab !== "all" ? `?type=${tab}` : ""}`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      if (usageRes.ok) setUsage(await usageRes.json());
      if (filesRes.ok) {
        const json = await filesRes.json();
        setFiles(json.files || []);
      }
    } catch (e) {
      console.error("Error fetching storage:", e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchData(); }, [tab]);

  async function handleDelete(fileId: string) {
    if (!confirm("¿Eliminar este archivo permanentemente?")) return;
    setDeleting(fileId);
    try {
      await fetch(`/api/storage/files/${fileId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchData();
    } catch (e) {
      console.error("Error deleting:", e);
    } finally {
      setDeleting(null);
    }
  }

  function downloadUrl(fileId: string, variant: string) {
    return `/api/storage/files/${fileId}/download?variant=${variant}`;
  }

  const tabs: { key: TabType; label: string; icon: any }[] = [
    { key: "all", label: "Todos", icon: Database },
    { key: "tickets", label: "Fotos de tickets", icon: Image },
    { key: "invoices", label: "Facturas", icon: FileText },
  ];

  const usageColor = usage
    ? usage.used_pct > 80 ? "from-rose-500 to-pink-500" : usage.used_pct > 50 ? "from-amber-500 to-orange-500" : "from-emerald-500 to-teal-500"
    : "from-primary-500 to-indigo-500";

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8 animate-slide-up">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Link href="/dashboard" className="p-2 rounded-xl hover:bg-[var(--surface-elevated)] text-[var(--text-secondary)]">
          <ChevronLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-[var(--text)] flex items-center gap-2">
            <HardDrive className="h-6 w-6 text-primary-500" />
            Almacenamiento
          </h1>
          <p className="text-sm text-[var(--text-secondary)]">Administra tus archivos guardados</p>
        </div>
      </div>

      {/* Usage bar */}
      {usage && (
        <div className="card p-5 mb-6">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
              <HardDrive className="h-4 w-4" />
              <span>Almacenamiento Iztack Finance</span>
            </div>
            <span className={`text-sm font-semibold ${usage.used_pct > 80 ? "text-rose-500" : usage.used_pct > 50 ? "text-amber-500" : "text-emerald-500"}`}>
              {usage.used_pct}% usado
            </span>
          </div>
          <div className="h-3 w-full bg-[var(--surface-elevated)] rounded-full overflow-hidden border border-[var(--border)] mb-2">
            <div
              className={`h-full rounded-full bg-gradient-to-r ${usageColor} transition-all duration-700`}
              style={{ width: `${Math.min(usage.used_pct, 100)}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-[var(--text-muted)]">
            <span>{(usage.used_bytes / 1024 / 1024).toFixed(1)} MB usados</span>
            <span>{(usage.max_bytes / 1024 / 1024 / 1024).toFixed(1)} GB total</span>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        {tabs.map((t) => {
          const Icon = t.icon;
          const active = tab === t.key;
          return (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all whitespace-nowrap ${
                active
                  ? "bg-primary-50 dark:bg-primary-500/15 text-primary-700 dark:text-primary-300 shadow-sm"
                  : "text-[var(--text-secondary)] hover:text-[var(--text)] hover:bg-[var(--surface-elevated)]"
              }`}
            >
              <Icon className="h-4 w-4" />
              {t.label}
              {active && files.length > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-primary-500/20">{files.length}</span>
              )}
            </button>
          );
        })}
        <button
          onClick={fetchData}
          className="ml-auto p-2.5 rounded-xl text-[var(--text-secondary)] hover:bg-[var(--surface-elevated)] transition-colors"
          title="Actualizar"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Files */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 text-primary-500 animate-spin" />
        </div>
      ) : files.length === 0 ? (
        <div className="card p-12 text-center">
          <div className="w-16 h-16 rounded-2xl bg-primary-50 dark:bg-primary-500/10 flex items-center justify-center mx-auto mb-4">
            <FolderOpen className="h-8 w-8 text-primary-500" />
          </div>
          <p className="text-lg font-medium text-[var(--text)] mb-1">Sin archivos</p>
          <p className="text-sm text-[var(--text-muted)]">
            {tab === "tickets"
              ? "Sube tu primer ticket para ver sus imágenes aquí."
              : tab === "invoices"
              ? "Las facturas generadas aparecerán aquí."
              : "Sube tickets y genera facturas para ver tus archivos."}
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {files.map((file) => (
            <div key={file.id} className="card p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-start gap-4 min-w-0">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${
                  file.type === "ticket"
                    ? "bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400"
                    : "bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400"
                }`}>
                  {file.type === "ticket" ? <Image className="h-6 w-6" /> : <FileText className="h-6 w-6" />}
                </div>
                <div className="min-w-0">
                  <p className="font-semibold text-[var(--text)] truncate">
                    {file.type === "ticket" ? `Ticket ${file.id.slice(0, 8)}...` : `Factura ${file.id.slice(0, 8)}...`}
                  </p>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">{formatDate(file.created_at)}</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {file.type === "ticket" && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-amber-50 dark:bg-amber-500/10 text-amber-700 dark:text-amber-300">
                        <Image className="h-3 w-3 inline mr-1" />
                        {formatBytes(file.original_size)}
                      </span>
                    )}
                    {file.type === "invoice" && file.has_pdf && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-300">
                        <File className="h-3 w-3 inline mr-1" />
                        PDF {formatBytes(file.pdf_size)}
                      </span>
                    )}
                    {file.type === "invoice" && file.has_xml && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300">
                        <File className="h-3 w-3 inline mr-1" />
                        XML {formatBytes(file.xml_size)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {file.type === "ticket" && (
                  <a
                    href={downloadUrl(file.id, "original")}
                    download
                    className="btn btn-secondary px-3 py-2 text-xs"
                    title="Descargar imagen"
                  >
                    <Download className="h-4 w-4" />
                  </a>
                )}
                {file.type === "invoice" && file.has_pdf && (
                  <a
                    href={downloadUrl(file.id, "pdf")}
                    download
                    className="btn btn-secondary px-3 py-2 text-xs"
                    title="Descargar PDF"
                  >
                    <File className="h-4 w-4" />
                    PDF
                  </a>
                )}
                {file.type === "invoice" && file.has_xml && (
                  <a
                    href={downloadUrl(file.id, "xml")}
                    download
                    className="btn btn-secondary px-3 py-2 text-xs"
                    title="Descargar XML"
                  >
                    <File className="h-4 w-4" />
                    XML
                  </a>
                )}
                <button
                  onClick={() => handleDelete(file.id)}
                  disabled={deleting === file.id}
                  className="btn btn-danger px-3 py-2 text-xs"
                  title="Eliminar"
                >
                  {deleting === file.id ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Trash2 className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

export default function StoragePage() {
  return (
    <AuthGuard>
      <AppNav />
      <StorageContent />
    </AuthGuard>
  );
}
