"use client";

import { useState, useRef, useEffect } from "react";
import { X, Upload, CheckCircle, AlertCircle, Loader2, Image as ImageIcon } from "lucide-react";

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
    const maxSize = 5 * 1024 * 1024; // 5MB
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
          if (oversized.length > 0) {
            setError(`⚠️ Los siguientes archivos exceden 5MB y fueron omitidos:\n${oversized.join("\n")}`);
          } else {
            setError(null);
          }
        }
      };
      reader.readAsDataURL(file);
    });
    // Reset input so same file can be selected again
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
    <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-auto max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b sticky top-0 bg-white z-10">
          <h2 className="text-lg font-semibold text-gray-900">Subir Ticket</h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-full">
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        <div className="p-6">
          {/* Upload button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="w-full flex items-center gap-4 p-6 border-2 border-dashed border-sky-300 rounded-xl hover:bg-sky-50 transition disabled:opacity-50"
          >
            <ImageIcon className="h-10 w-10 text-sky-600 shrink-0" />
            <div className="text-left">
              <p className="font-medium text-gray-900 text-lg">Seleccionar imágenes</p>
              <p className="text-sm text-gray-500 mt-1">JPEG, PNG o WEBP (máx. 5MB c/u)</p>
              <p className="text-xs text-gray-400 mt-0.5">En iOS: elige "Tomar Foto" para usar la cámara nativa</p>
            </div>
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            multiple
            className="hidden"
            onChange={handleFileSelect}
            capture="environment"
          />

          {/* Selected images preview */}
          {images.length > 0 && (
            <div className="mt-4 space-y-2">
              <p className="text-sm font-medium text-gray-700">
                {images.length} imagen(es) seleccionada(s):
              </p>
              <div className="grid grid-cols-3 gap-2">
                {images.map((img, i) => (
                  <div key={i} className="relative group">
                    <img
                      src={img.dataUrl}
                      alt={`Ticket ${i + 1}`}
                      className="w-full h-24 object-cover rounded-lg border"
                    />
                    <button
                      onClick={() => removeImage(i)}
                      className="absolute -top-1.5 -right-1.5 p-0.5 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition hover:bg-red-600"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                    <p className="text-[10px] text-gray-500 truncate mt-0.5">{img.file.name}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
              <div className="flex gap-2">
                <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
                <p className="text-sm text-red-700 whitespace-pre-line">{error}</p>
              </div>
            </div>
          )}

          {/* Success result */}
          {result?.success && (
            <div className="mt-4 bg-green-50 border border-green-200 rounded-lg px-4 py-3">
              <div className="flex gap-2">
                <CheckCircle className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-green-800">{result.message}</p>
                  {result.data?.store_name && (
                    <p className="text-xs text-green-600 mt-1">🏪 {result.data.store_name}</p>
                  )}
                  {result.data?.total_amount && (
                    <p className="text-xs text-green-600">💰 ${result.data.total_amount.toFixed(2)}</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Error result */}
          {result?.success === false && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
              <div className="flex gap-2">
                <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-red-800">❌ Error al procesar</p>
                  <p className="text-sm text-red-600 mt-1">{result.message}</p>
                </div>
              </div>
            </div>
          )}

          {/* Submit button */}
          {images.length > 0 && !result?.success && (
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="mt-4 w-full py-3 bg-sky-600 text-white rounded-lg font-medium hover:bg-sky-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {uploading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Subiendo {images.length} imagen(es)...
                </>
              ) : (
                <>
                  <Upload className="h-5 w-5" />
                  Subir {images.length} ticket(s)
                </>
              )}
            </button>
          )}

          {/* Close button after success */}
          {result?.success && (
            <button
              onClick={onClose}
              className="mt-4 w-full py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700"
            >
              Cerrar
            </button>
          )}
        </div>
      </div>
    </div>
  );
}