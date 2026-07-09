"use client";

import { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send, Camera, Paperclip } from "lucide-react";

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

  // Load history when opened
  useEffect(() => {
    if (isOpen && !hasHistory) {
      loadHistory();
    }
  }, [isOpen]);

  // Scroll to bottom on new messages
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
    } catch (e) {
      console.error("Error loading chat history:", e);
    }
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

      // Optimistically add user message
      const userMsg: Message = {
        id: Date.now().toString(),
        role: "user",
        content: file ? "📸 Imagen enviada" : msgText.trim(),
        msg_type: "text",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setInput("");

      const res = await fetch("/api/chat/message", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        // Reload full history to get proper message IDs
        await loadHistory();
      } else {
        const errMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "bot",
          content: "❌ Error al enviar mensaje. Intenta de nuevo.",
          msg_type: "error",
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errMsg]);
      }
    } catch (e) {
      const errMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "bot",
        content: "❌ Error de conexión.",
        msg_type: "error",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  }

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      sendMessage(undefined, file);
    }
  }

  function formatContent(content: string): string {
    // Convert markdown-like syntax to simple HTML for display
    return content
      .replace(/\*([^*]+)\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br />");
  }

  return (
    <>
      {/* Toggle button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-40 w-14 h-14 bg-sky-600 text-white rounded-full shadow-lg hover:bg-sky-700 flex items-center justify-center transition-all"
      >
        {isOpen ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </button>

      {/* Chat window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-40 w-80 sm:w-96 h-[500px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden border">
          {/* Header */}
          <div className="bg-sky-600 text-white px-4 py-3 flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            <span className="font-semibold">Asistente Iztack</span>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 text-sm mt-8">
                <p className="text-3xl mb-2">🤖</p>
                <p>¡Hola! Soy tu asistente financiero.</p>
                <p className="mt-1">Puedes enviarme fotos de tickets o escribirme comandos.</p>
                <p className="mt-3 text-xs">
                  Ej: "hola", "/ayuda", "/status"
                </p>
              </div>
            )}

            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] px-3 py-2 rounded-xl text-sm ${
                    msg.role === "user"
                      ? "bg-sky-600 text-white rounded-br-sm"
                      : "bg-white text-gray-800 rounded-bl-sm shadow-sm border"
                  }`}
                  dangerouslySetInnerHTML={{ __html: formatContent(msg.content) }}
                />
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-white px-3 py-2 rounded-xl text-sm shadow-sm border">
                  <span className="animate-pulse">Escribiendo...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t p-3 bg-white">
            <div className="flex gap-2">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="p-2 text-gray-400 hover:text-gray-600"
              >
                <Camera className="h-5 w-5" />
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={handleFileSelect}
              />
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Escribe un mensaje..."
                className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500"
                disabled={loading}
              />
              <button
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
                className="p-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 disabled:opacity-50"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}