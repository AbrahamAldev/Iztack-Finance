"use client";

export default function ShoppingListPage() {
  return (
    <div className="text-center py-12">
      <div className="text-6xl mb-4">🛒</div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Lista de Compras</h1>
      <p className="text-gray-500 max-w-md mx-auto">
        Tu lista de compras inteligente aparecerá aquí.
        El sistema detectará automáticamente tus ciclos de consumo.
      </p>
    </div>
  );
}