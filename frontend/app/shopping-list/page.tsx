"use client";

import AuthGuard from "../components/AuthGuard";
import AppNav from "../components/AppNav";

function ShoppingListContent() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Lista de Compras</h1>
      <p className="text-sm text-gray-500 mb-8">
        Tu lista de compras inteligente generada automáticamente
      </p>
      <div className="text-center py-12 bg-white rounded-lg shadow">
        <div className="text-6xl mb-4">🛒</div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Lista de Compras</h2>
        <p className="text-gray-500 max-w-md mx-auto">
          Tu lista de compras inteligente aparecerá aquí.
          El sistema detectará automáticamente tus ciclos de consumo.
        </p>
      </div>
    </div>
  );
}

export default function ShoppingListPage() {
  return (
    <AuthGuard>
      <AppNav />
      <ShoppingListContent />
    </AuthGuard>
  );
}