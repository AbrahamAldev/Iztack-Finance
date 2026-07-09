"use client";

import { useState, useRef, useCallback } from "react";
import { Camera, Upload, X, ChevronLeft, ChevronRight, Check, Image as ImageIcon } from "lucide-react";

interface CapturedImage {
  dataUrl: string;
  file: File;
}

interface Props {
  onClose: () => void;
}

export default function TicketUpload({ onClose }: Props) {
  const [mode, setMode] = useState<"select" | "camera" | "preview">("select");
  const [images, setImages] = useState<CapturedImage[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isContinuation, setIsContinuation] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1920 }, height: { ideal: 1080 } },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.setAttribute("playsinline", "true");
        videoRef.current.setAttribute("autoplay", "true");
        videoRef.current.setAttribute("muted", "true");
        await videoRef.current.play();
      }
      setMode("camera");
    } catch (err) {
      setError("No se pudo acceder a la cámara. Verifica los permisos.");
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  }, []);

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0);
    canvas.toBlob((blob) => {
      if (!blob) return;
      const file = new File([blob], `ticket_${Date.now()}.jpg`, { type: "image/jpeg" });
      const dataUrl = canvas.toDataURL("image/jpeg", 0.9);
      setImages((prev) => [...prev, { dataUrl, file }]);
    }, "image/jpeg", 0.9);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const newImages: CapturedImage[] = [];
    files.forEach((file) => {
      if (file.size > 10 * 1024 * 1024) return;
      const reader = new FileReader();
      reader.onload = () => {
        newImages.push({ dataUrl: reader.result as string, file });
        if (newImages.length === files.length) {
          setImages((prev) => [...prev, ...newImages]);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const removeImage = (index: number) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
    if (currentIndex >= images.length - 1) {
      setCurrentIndex(Math.max(0, images.length - 2));
    }
  };

  const handleUpload = async () => {
    if (images.length === 0) return;
    setUploading(true);
    setError(null);
    const token = localStorage.getItem("iztack_token");
    if (!token) { setError("Debes iniciar sesión"); setUploading(false); return; }
    try {
      const formData = new FormData();
      images.forEach((img) => formData.append("files", img.file));
      formData.append("is_continuation", String(isContinuation));
      const res = await fetch("/api/tickets/upload", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const data = await res.json();
      if (data.success) setResult(data);
      else setError(data.error || "Error al procesar el ticket");
    } catch (err) {
      setError("Error de conexión con el servidor");
    } finally { setUploading(false); }
  };

  const reset = () => { stopCamera(); setImages([]); setCurrentIndex(0); setResult(null); setError(null); setMode("select"); };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 max-h-[95vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b sticky top-0 bg-white z-10">
          <h2 className="text-lg font-semibold text-gray-900">Subir Ticket</h2>
          <button onClick={() => { stopCamera(); onClose(); }} className="p-1 hover:bg-gray-100 rounded-full">
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {mode === "select" && (
          <div className="p-6 space-y-4">
            <button onClick={startCamera} className="w-full flex items-center gap-3 p-6 border-2 border-dashed border-sky-300 rounded-xl hover:bg-sky-50 transition">
              <Camera className="h-10 w-10 text-sky-600" />
              <div className="text-left">
                <p className="font-medium text-gray-900 text-lg">Tomar foto</p>
                <p className="text-sm text-gray-500">Usa la cámara para capturar el ticket</p>
              </div>
            </button>
            <button onClick={() => fileInputRef.current?.click()} className="w-full flex items-center gap-3 p-6 border-2 border-dashed border-gray-300 rounded-xl hover:bg-gray-50 transition">
              <ImageIcon className="h-10 w-10 text-gray-600" />
              <div className="text-left">
                <p className="font-medium text-gray-900 text-lg">Seleccionar archivos</p>
                <p className="text-sm text-gray-500">JPEG, PNG o WEBP (máx. 10MB c/u)</p>
              </div>
            </button>
            <input ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/webp" multiple className="hidden" onChange={handleFileSelect} />
            {images.length > 0 && (
              <div className="pt-4 border-t">
                <p className="text-sm font-medium text-gray-700 mb-2">{images.length} imagen(es) seleccionada(s)</p>
                <label className="flex items-center gap-2 text-sm text-gray-600 mb-3">
                  <input type="checkbox" checked={isContinuation} onChange={(e) => setIsContinuation(e.target.checked)} className="rounded" />
                  Son continuaciones del mismo ticket
                </label>
                <button onClick={() => setMode("preview")} className="w-full py-3 bg-sky-600 text-white rounded-lg font-medium hover:bg-sky-700">Revisar y subir</button>
              </div>
            )}
          </div>
        )}

        {mode === "camera" && (
          <div className="relative bg-black" style={{ minHeight: "70vh" }}>
            <video ref={videoRef} autoPlay playsInline muted className="w-full h-full min-h-[70vh] object-cover" />
            <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
              <div className="w-[85%] h-[70%] border-2 border-white/50 rounded-lg relative">
                <div className="absolute top-2 left-4 text-xs text-white/70">Coloca el ticket dentro del marco</div>
                <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-sky-400" />
                <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-sky-400" />
                <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-sky-400" />
                <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-sky-400" />
              </div>
            </div>
            {isContinuation && <div className="absolute top-4 right-4 bg-black/60 text-white text-xs px-3 py-1 rounded-full">Toma {images.length + 1}/3</div>}
            <canvas ref={canvasRef} className="hidden" />
            <div className="flex items-center justify-center gap-6 p-4 bg-gray-900">
              <button onClick={() => { stopCamera(); setMode("select"); }} className="text-white/70 hover:text-white text-sm">Cancelar</button>
              <button onClick={capturePhoto} className="w-20 h-20 rounded-full border-4 border-white flex items-center justify-center hover:scale-105 transition">
                <div className="w-14 h-14 rounded-full bg-white" />
              </button>
              <button onClick={() => { stopCamera(); setMode("preview"); }} className="text-white/70 hover:text-white text-sm">{images.length > 0 ? "Listo" : "Saltar"}</button>
            </div>
          </div>
        )}

        {mode === "preview" && (
          <div className="p-4">
            {images.length === 0 ? (
              <p className="text-center text-gray-500 py-8">No hay imágenes para revisar</p>
            ) : (
              <>
                <div className="relative mb-4">
                  <img src={images[currentIndex].dataUrl} alt={`Ticket ${currentIndex + 1}`} className="w-full h-80 object-contain bg-gray-100 rounded-lg" />
                  {images.length > 1 && (
                    <>
                      <button onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))} disabled={currentIndex === 0} className="absolute left-2 top-1/2 -translate-y-1/2 p-2 bg-black/40 text-white rounded-full disabled:opacity-30"><ChevronLeft className="h-6 w-6" /></button>
                      <button onClick={() => setCurrentIndex((i) => Math.min(images.length - 1, i + 1))} disabled={currentIndex === images.length - 1} className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-black/40 text-white rounded-full disabled:opacity-30"><ChevronRight className="h-6 w-6" /></button>
                    </>
                  )}
                  <span className="absolute bottom-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded">{currentIndex + 1}/{images.length}</span>
                </div>
                <div className="flex gap-2 overflow-x-auto pb-2 mb-3">
                  {images.map((img, i) => (
                    <div key={i} className="relative flex-shrink-0">
                      <img src={img.dataUrl} alt="" className={`w-20 h-20 object-cover rounded-lg cursor-pointer ${i === currentIndex ? "ring-2 ring-sky-500" : ""}`} onClick={() => setCurrentIndex(i)} />
                      <button onClick={() => removeImage(i)} className="absolute -top-1 -right-1 p-0.5 bg-red-500 text-white rounded-full"><X className="h-3 w-3" /></button>
                    </div>
                  ))}
                </div>
                <label className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                  <input type="checkbox" checked={isContinuation} onChange={(e) => setIsContinuation(e.target.checked)} className="rounded" />
                  Son continuaciones del mismo ticket (se unirán automáticamente)
                </label>
                {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm mb-4">{error}</div>}
                {result && (
                  <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm mb-4">
                    <p className="font-semibold">✅ Ticket procesado</p>
                    {result.data?.store_name && <p>Tienda: {result.data.store_name}</p>}
                    {result.data?.total_amount && <p>Total: ${result.data.total_amount.toFixed(2)}</p>}
                    <p className="text-xs mt-1">{result.message}</p>
                  </div>
                )}
                <div className="flex gap-3">
                  <button onClick={reset} className="flex-1 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50">Tomar más fotos</button>
                  <button onClick={handleUpload} disabled={uploading} className="flex-1 py-3 bg-sky-600 text-white rounded-lg font-medium hover:bg-sky-700 disabled:opacity-50">{uploading ? "Subiendo..." : "Subir ticket"}</button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}