"use client";

import { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send, Camera, AlertTriangle, Bot, User } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "bot";
  content: string;
  msg_type: string;
  created_at: string;
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [hasHistory, setHasHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen && !hasHistory) loadHistory();
  }, [isOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function loadHistory() {
    const token = localStorage.getItem("iztack_token");
    if (!token) return;
    try {
      const res = await fetch("/api/chat/history?limit=30", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages || []);
        setHasHistory(true);
      }
    } catch (e) { console.error(e); }
  }

  async function sendMessage(text?: string, file?: File) {
    const token = localStorage.getItem("iztack_token");
    if (!token) return;
    const msgText = text || input;
    if (!msgText.trim() && !file) return;
    setLoading(true);
    try {
      const formData = new FormData();
      if (msgText.trim()) formData.append("text", msgText.trim());
      if (file) formData.append("file", file);
      const userMsg: Message = {
        id: Date.now().toString(), role: "user",
        content: file ? "📸 Imagen enviada" : msgText.trim(),
        msg_type: "text", created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setInput("");
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000);
      const res = await fetch("/api/chat/message", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      if (res.ok) {
        await loadHistory();
      } else if (res.status === 401) {
        localStorage.removeItem("iztack_token");
        window.location.href = "/login";
      } else {
        let detail = "❌ Error al procesar el mensaje.";
        try {
          const errData = await res.json();
          detail = errData.detail || detail;
        } catch {}
        setMessages((prev) => [...prev, {
          id: (Date.now() + 1).toString(), role: "bot",
          content: detail,
          msg_type: "error", created_at: new Date().toISOString(),
        }]);
      }
    } catch (e: any) {
      setMessages((prev) => [...prev, {
        id: (Date.now() + 1).toString(), role: "bot",
        content: e.name === "AbortError"
          ? "⏱️ El servicio de IA tardó demasiado. Los modelos gratuitos pueden ser lentos; intenta de nuevo."
          : "❌ Error de conexión.",
        msg_type: "error",
        created_at: new Date().toISOString(),
      }]);
    } finally { setLoading(false); }
  }

  async function sendReport() {
    const description = prompt("Describe brevemente el error:\n• ¿Qué estabas haciendo?\n• ¿Qué error viste?");
    if (!description) return;
    const token = localStorage.getItem("iztack_token");
    if (!token) return;
    try {
      await fetch("/api/chat/report", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ message: description }),
      });
      setMessages((prev) => [...prev, {
        id: (Date.now() + 1).toString(), role: "bot",
        content: "✅ Reporte enviado al equipo de soporte. Gracias por ayudar a mejorar.",
        msg_type: "info", created_at: new Date().toISOString(),
      }]);
    } catch (e) {
      setMessages((prev) => [...prev, {
        id: (Date.now() + 1).toString(), role: "bot",
        content: "❌ No se pudo enviar el reporte.", msg_type: "error",
        created_at: new Date().toISOString(),
      }]);
    }
  }

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) sendMessage(undefined, file);
  }

  function formatContent(content: string): string {
    return content
      .replace(/\*\*(.*?)\*\*/g, "<strong class='text-[var(--text)]'>$1</strong>")
      .replace(/\n/g, "<br />");
  }

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-2xl gradient-bg text-white shadow-glow hover:scale-110 flex items-center justify-center transition-all"
      >
        {isOpen ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </button>
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-40 w-[90vw] max-w-[400px] h-[540px] card flex flex-col overflow-hidden animate-slide-up">
          <div className="gradient-bg text-white px-5 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                <Bot className="h-6 w-6" />
              </div>
              <div>
                <p className="font-semibold">Asistente Iztack</p>
                <p className="text-xs text-white/80">Siempre listo para ayudarte</p>
              </div>
            </div>
            <button onClick={sendReport} className="p-2 hover:bg-white/10 rounded-lg transition-colors" title="Reportar error">
              <AlertTriangle className="h-4 w-4" />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-[var(--background)]">
            {messages.length === 0 && (
              <div className="text-center text-[var(--text-muted)] mt-10">
                <div className="w-16 h-16 rounded-2xl bg-primary-50 dark:bg-primary-500/10 flex items-center justify-center mx-auto mb-4">
                  <Bot className="h-8 w-8 text-primary-500" />
                </div>
                <p className="font-medium text-[var(--text)]">¡Hola!</p>
                <p className="text-sm mt-1">Soy tu asistente financiero.</p>
                <p className="text-xs mt-3 opacity-80">Puedo ver tus tickets, gastos y más.</p>
              </div>
            )}
            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                {msg.role === "bot" && (
                  <div className="w-7 h-7 rounded-full gradient-bg flex items-center justify-center mr-2 mt-1 shrink-0">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-primary-600 text-white rounded-br-md"
                      : msg.msg_type === "error"
                      ? "bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-300 border border-red-100 dark:border-red-500/20 rounded-bl-md"
                      : "bg-[var(--surface-elevated)] text-[var(--text)] border border-[var(--border)] rounded-bl-md shadow-sm"
                  }`}
                  dangerouslySetInnerHTML={{ __html: formatContent(msg.content) }}
                />
                {msg.role === "user" && (
                  <div className="w-7 h-7 rounded-full bg-surface-300 dark:bg-surface-600 flex items-center justify-center ml-2 mt-1 shrink-0">
                    <User className="h-4 w-4 text-[var(--text)]" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="w-7 h-7 rounded-full gradient-bg flex items-center justify-center mr-2 mt-1 shrink-0">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <div className="bg-[var(--surface-elevated)] border border-[var(--border)] px-4 py-3 rounded-2xl rounded-bl-md shadow-sm">
                  <span className="flex gap-1">
                    <span className="w-2 h-2 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-2 h-2 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-2 h-2 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: "300ms" }} />
                  </span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <div className="border-t border-[var(--border)] p-3 bg-[var(--surface)]">
            <div className="flex gap-2">
              <button onClick={() => fileInputRef.current?.click()} className="p-2.5 text-[var(--text-muted)] hover:text-primary-600 dark:hover:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-500/10 rounded-xl transition-colors">
                <Camera className="h-5 w-5" />
              </button>
              <input ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={handleFileSelect} />
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Escribe un mensaje..."
                className="input flex-1"
                disabled={loading}
              />
              <button onClick={() => sendMessage()} disabled={loading || !input.trim()} className="p-2.5 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-40 transition-colors">
                <Send className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
