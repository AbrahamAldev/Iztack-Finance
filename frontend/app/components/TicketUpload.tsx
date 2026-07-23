"use client";

import { useState, useRef } from "react";
import { X, Upload, CheckCircle, AlertCircle, Loader2, Image as ImageIcon, Camera, Trash2 } from "lucide-react";

interface CapturedImage {
  dataUrl: string;
  file: File;
}

interface Props {
  onClose: () => void;
}

export default function TicketUpload({ onClose }: Props) {
  const [images, setImages] = useState<CapturedImage[]>([]);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string; data?: any } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const maxSize = 5 * 1024 * 1024;
    const oversized: string[] = [];
    const newImages: CapturedImage[] = [];

    files.forEach((file) => {
      if (file.size > maxSize) {
        oversized.push(file.name);
        return;
      }
      const reader = new FileReader();
      reader.onload = () => {
        newImages.push({ dataUrl: reader.result as string, file });
        if (newImages.length + oversized.length === files.length) {
          setImages((prev) => [...prev, ...newImages]);
          setError(oversized.length > 0
            ? `⚠️ Estos archivos exceden 5MB y fueron omitidos:\n${oversized.join("\n")}`
            : null);
        }
      };
      reader.readAsDataURL(file);
    });
    e.target.value = "";
  };

  const removeImage = (index: number) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (images.length === 0) return;
    setUploading(true);
    setError(null);
    setResult(null);

    const token = localStorage.getItem("iztack_token");
    if (!token) {
      setError("Debes iniciar sesión para subir tickets.");
      setUploading(false);
      return;
    }

    try {
      const formData = new FormData();
      images.forEach((img) => formData.append("files", img.file));
      formData.append("is_continuation", "false");

      const res = await fetch("/api/tickets/upload", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      const data = await res.json();

      if (data.success) {
        setResult({
          success: true,
          message: `✅ ${images.length} ticket(s) procesado(s) correctamente.`,
          data: data.data,
        });
        setImages([]);
      } else {
        setResult({
          success: false,
          message: data.error || "Error al procesar el ticket.",
        });
      }
    } catch (err) {
      setError("Error de conexión con el servidor. Verifica tu internet.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
      <div className="card w-full max-w-xl max-h-[90vh] overflow-y-auto animate-slide-up">
        <div className="flex items-center justify-between p-6 border-b border-[var(--border)] sticky top-0 bg-[var(--surface)] z-10 rounded-t-2xl">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary-50 dark:bg-primary-500/10 flex items-center justify-center text-primary-600 dark:text-primary-400">
              <Camera className="h-5 w-5" />
            </div>
            <h2 className="text-xl font-bold text-[var(--text)]">Subir ticket</h2>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-[var(--surface-elevated)] rounded-xl transition-colors">
            <X className="h-5 w-5 text-[var(--text-muted)]" />
          </button>
        </div>

        <div className="p-6">
          <div className="bg-primary-50 dark:bg-primary-500/10 border border-primary-100 dark:border-primary-500/20 rounded-xl p-4 mb-5 text-sm text-primary-800 dark:text-primary-200">
            <p className="font-semibold mb-2 flex items-center gap-2"><Upload className="h-4 w-4" /> ¿Cómo subir tickets?</p>
            <ul className="space-y-1.5 text-[var(--text-secondary)]">
              <li>• Puedes subir <strong className="text-[var(--text)]">varios tickets diferentes</strong> al mismo tiempo.</li>
              <li>• Para tickets largos, sube solo fotos de <strong className="text-[var(--text)]">ese mismo ticket</strong> como continuación.</li>
              <li className="text-xs text-[var(--text-muted)]">No mezcles tickets diferentes marcando continuación.</li>
            </ul>
          </div>

          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="w-full flex items-center gap-5 p-6 border-2 border-dashed border-primary-300 dark:border-primary-500/30 rounded-2xl hover:bg-primary-50 dark:hover:bg-primary-500/5 transition disabled:opacity-50 group"
          >
            <div className="w-14 h-14 rounded-2xl bg-primary-100 dark:bg-primary-500/10 flex items-center justify-center text-primary-600 dark:text-primary-400 group-hover:scale-110 transition-transform">
              <ImageIcon className="h-7 w-7" />
            </div>
            <div className="text-left">
              <p className="font-semibold text-[var(--text)] text-lg">Seleccionar imágenes</p>
              <p className="text-sm text-[var(--text-muted)] mt-0.5">Galería, cámara o archivos</p>
              <p className="text-xs text-[var(--text-muted)] mt-1">JPEG, PNG o WEBP · máx. 5MB por imagen</p>
            </div>
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            multiple
            className="hidden"
            onChange={handleFileSelect}
          />

          {images.length > 0 && (
            <div className="mt-5">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-semibold text-[var(--text)]">
                  {images.length} imagen(es) seleccionada(s)
                </p>
                <button onClick={() => setImages([])} className="text-xs text-red-500 hover:text-red-600 flex items-center gap-1">
                  <Trash2 className="h-3 w-3" /> Limpiar
                </button>
              </div>
              <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
                {images.map((img, i) => (
                  <div key={i} className="relative group">
                    <img
                      src={img.dataUrl}
                      alt={`Ticket ${i + 1}`}
                      className="w-full h-24 object-cover rounded-xl border border-[var(--border)]"
                    />
                    <button
                      onClick={() => removeImage(i)}
                      className="absolute -top-2 -right-2 p-1.5 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition hover:bg-red-600 shadow-lg"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                    <p className="text-[10px] text-[var(--text-muted)] truncate mt-1">{img.file.name}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {error && (
            <div className="mt-5 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-xl px-4 py-3 flex gap-3 animate-fade-in">
              <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
              <p className="text-sm text-red-700 dark:text-red-300 whitespace-pre-line">{error}</p>
            </div>
          )}

          {result?.success && (
            <div className="mt-5 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl px-4 py-3 flex gap-3 animate-fade-in">
              <CheckCircle className="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-emerald-800 dark:text-emerald-300">{result.message}</p>
                {result.data?.store_name && (
                  <p className="text-xs text-emerald-700 dark:text-emerald-400 mt-1">🏪 {result.data.store_name}</p>
                )}
                {result.data?.total_amount && (
                  <p className="text-xs text-emerald-700 dark:text-emerald-400">💰 ${result.data.total_amount.toFixed(2)}</p>
                )}
              </div>
            </div>
          )}

          {result?.success === false && (
            <div className="mt-5 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-xl px-4 py-3 flex gap-3 animate-fade-in">
              <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-red-800 dark:text-red-300">❌ Error al procesar</p>
                <p className="text-sm text-red-700 dark:text-red-300 mt-1">{result.message}</p>
              </div>
            </div>
          )}

          {images.length > 0 && !result?.success && (
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="btn btn-primary w-full mt-6 py-3"
            >
              {uploading ? (
                <><Loader2 className="h-5 w-5 animate-spin" /> Subiendo {images.length} imagen(es)...</>
              ) : (
                <><Upload className="h-5 w-5" /> Subir {images.length} ticket(s)</>
              )}
            </button>
          )}

          {result?.success && (
            <button onClick={onClose} className="btn btn-primary w-full mt-6 py-3">
              <CheckCircle className="h-5 w-5" /> Cerrar
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
