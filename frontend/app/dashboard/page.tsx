"use client";

import { useState } from "react";
import AuthGuard from "../components/AuthGuard";
import AppNav from "../components/AppNav";
import TicketUpload from "../components/TicketUpload";

function DashboardContent() {
  const [showUpload, setShowUpload] = useState(false);

  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">Dashboard</h1>
          <p className="text-sm text-gray-500">
            Resumen de tus finanzas y estado del sistema
          </p>
        </div>
        <button
          onClick={() => setShowUpload(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-sky-600 text-white rounded-lg font-medium hover:bg-sky-700 shadow-sm transition-all"
        >
          <span className="text-lg">📸</span>
          Subir Ticket
        </button>
      </div>

      {showUpload && <TicketUpload onClose={() => setShowUpload(false)} />}

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-500 mb-1">Gastos del Mes</p>
          <p className="text-2xl font-bold text-gray-900">$0</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-500 mb-1">Ticket Promedio</p>
          <p className="text-2xl font-bold text-gray-900">$0</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-500 mb-1">Facturas Pendientes</p>
          <p className="text-2xl font-bold text-yellow-600">0</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-500 mb-1">Garantías Activas</p>
          <p className="text-2xl font-bold text-green-600">0</p>
        </div>
      </div>

      {/* Info */}
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <div className="text-6xl mb-4">📸</div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Envía un ticket por Telegram
        </h2>
        <p className="text-gray-500 max-w-md mx-auto">
          Toma una foto de tu ticket de compra y envíala al bot de Telegram.
          El sistema procesará el OCR, solicitará la factura CFDI y
          organizará todo automáticamente.
        </p>
        <div className="mt-6 inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm">
          <span>🤖</span>
          <span>Busca @Iztack_Finance_Bot en Telegram</span>
        </div>
      </div>

      {/* Status */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Conexiones</h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">API Backend</span>
              <span className="text-sm text-green-600 font-medium">● Activo</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Base de Datos</span>
              <span className="text-sm text-green-600 font-medium">● Conectada</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Bot Telegram</span>
              <span className="text-sm text-yellow-600 font-medium">● Configurar</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Accesos Rápidos</h3>
          <div className="space-y-2">
            <a href="/api/health" className="block text-sm text-blue-600 hover:underline">
              → Health Check API
            </a>
            <a href="/settings" className="block text-sm text-blue-600 hover:underline">
              → Configuración
            </a>
            <a href="/shopping-list" className="block text-sm text-blue-600 hover:underline">
              → Lista de Compras
            </a>
          </div>
        </div>
      </div>
    </>
  );
}

export default function DashboardPage() {
  return (
    <AuthGuard>
      <AppNav />
      <DashboardContent />
    </AuthGuard>
  );
}