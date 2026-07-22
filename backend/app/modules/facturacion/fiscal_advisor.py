"""Iztack-Finance - Fiscal Advisor. IA para recomendar tipo de gasto según régimen fiscal en México."""
import logging
from typing import Dict, Any, List
from app.utils.llm import LLMClient

logger = logging.getLogger(__name__)

# Regímenes fiscales comunes en México
REGIMEN_GASTO_MAP = {
    "sueldos_y_salarios": ["Gastos en general"],
    "honorarios": ["Gastos en general", "Gastos médicos", "Gastos funerarios", "Donativos"],
    "resico": ["Gastos en general", "Adquisición de mercancías", "Gastos de operación"],
    "actividades_empresariales": ["Adquisición de mercancías", "Gastos en general", "Gastos de operación", "Inversiones"],
    "arrendamiento": ["Gastos en general", "Gastos de operación"],
    "incorporacion_fiscal": ["Gastos en general", "Adquisición de mercancías"],
}

class FiscalAdvisor:
    """Recommends the best 'gasto' type for CFDI billing based on fiscal regime and products."""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def get_user_fiscal_data(self, user_id: str) -> Dict[str, Any]:
        """Get stored fiscal data for a user (stub)."""
        return {
            "rfc": "",
            "razon_social": "",
            "codigo_postal": "",
            "regimen_fiscal": "",
        }

    async def recommend_gasto_type(
        self, regimen: str, products: List[str], store_name: str
    ) -> Dict[str, Any]:
        """Recommend the best gasto type based on fiscal regime."""
        if not regimen or not products:
            return {"gasto_type": "Gastos en general", "reason": "Gasto general por defecto", "auto": True}

        # Try LLM recommendation
        prompt = (
            f"Eres un asesor fiscal mexicano. Para un contribuyente en régimen '{regimen}' "
            f"que compró en '{store_name}' los productos: {', '.join(products)}.\n"
            "Responde SOLO en formato JSON: {\"gasto\": \"tipo de gasto\", \"razon\": \"breve explicación\"}"
        )
        
        try:
            response = await self.llm.chat(user_message=prompt, max_tokens=150, temperature=0.0)
            import json
            data = json.loads(response)
            return {"gasto_type": data.get("gasto", "Gastos en general"), "reason": data.get("razon", ""), "auto": True}
        except Exception:
            return {"gasto_type": "Gastos en general", "reason": "Recomendación por defecto", "auto": True}