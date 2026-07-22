"""
Iztack-Finance - Fiscal Service (México)
Processes Constancia de Situación Fiscal (PDF), manages fiscal data,
and provides deduction recommendations based on Mexican tax law.
"""
import logging
import base64
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import FiscalData
from app.utils.llm import LLMClient

logger = logging.getLogger(__name__)

# Mexican tax regime deduction rules (LISR Art. 151)
REGIME_DEDUCTIONS = {
    "sueldos_y_salarios": {
        "max_deductions": "15% del ingreso o 5 UMAS anuales ($198,034 aprox)",
        "allowed": [
            "Honorarios médicos y dentales",
            "Gastos hospitalarios",
            "Medicinas (en hospital)",
            "Gastos funerarios",
            "Donativos",
            "Intereses reales de créditos hipotecarios",
            "Aportaciones voluntarias al SAR / AFORE",
            "Colegiaturas (preescolar a bachillerato)",
            "Transporte escolar",
            "Primas de seguros de gastos médicos",
        ],
    },
    "honorarios": {
        "max_deductions": "Gastos necesarios para la actividad",
        "allowed": [
            "Gastos en general",
            "Gastos médicos y hospitalarios",
            "Gastos funerarios",
            "Donativos",
            "Intereses hipotecarios",
        ],
    },
    "resico": {
        "max_deductions": "No aplican deducciones personales (régimen simplificado)",
        "allowed": ["Adquisición de mercancías", "Gastos de operación", "Devoluciones y descuentos"],
    },
    "actividades_empresariales": {
        "max_deductions": "Gastos estrictamente necesarios para la actividad",
        "allowed": [
            "Adquisición de mercancías",
            "Gastos de operación",
            "Devoluciones y descuentos",
            "Inversiones",
            "Cuotas patronales IMSS",
        ],
    },
}

class FiscalService:
    """Manages fiscal data and provides tax recommendations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_fiscal_data(self, user_id: str) -> Optional[Dict]:
        """Get stored fiscal data for a user."""
        from sqlalchemy import select
        result = await self.db.execute(
            select(FiscalData).where(FiscalData.user_id == user_id)
        )
        fd = result.scalar_one_or_none()
        if not fd:
            return None
        return {
            "rfc": fd.rfc,
            "razon_social": fd.razon_social,
            "codigo_postal": fd.codigo_postal,
            "regimen_fiscal": fd.regimen_fiscal,
            "direccion": fd.direccion,
        }

    async def save_fiscal_data(self, user_id: str, data: Dict) -> Dict:
        """Save fiscal data for a user."""
        from sqlalchemy import select
        result = await self.db.execute(
            select(FiscalData).where(FiscalData.user_id == user_id)
        )
        fd = result.scalar_one_or_none()
        if not fd:
            fd = FiscalData(user_id=user_id)
            self.db.add(fd)
        fd.rfc = data.get("rfc", fd.rfc)
        fd.razon_social = data.get("razon_social", fd.razon_social)
        fd.codigo_postal = data.get("codigo_postal", fd.codigo_postal)
        fd.regimen_fiscal = data.get("regimen_fiscal", fd.regimen_fiscal)
        fd.direccion = data.get("direccion", fd.direccion)
        await self.db.commit()
        await self.db.refresh(fd)
        return {
            "rfc": fd.rfc,
            "razon_social": fd.razon_social,
            "codigo_postal": fd.codigo_postal,
            "regimen_fiscal": fd.regimen_fiscal,
            "direccion": fd.direccion,
        }

    async def process_csf(self, user_id: str, pdf_bytes: bytes) -> Dict:
        """Process a CSF PDF and extract fiscal data using LLM."""
        # Store the PDF (base64)
        b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

        from sqlalchemy import select
        result = await self.db.execute(
            select(FiscalData).where(FiscalData.user_id == user_id)
        )
        fd = result.scalar_one_or_none()
        if not fd:
            fd = FiscalData(user_id=user_id)
            self.db.add(fd)

        fd.csd_pdf_base64 = b64_pdf
        fd.csd_uploaded_at = __import__("datetime").datetime.utcnow()

        # Try to extract data using LLM (OpenRouter GPT-4o-mini)
        try:
            import os
            api_key = os.environ.get("OPENROUTER_API_KEY", "")
            if api_key:
                llm = LLMClient(api_key)
                prompt = (
                    "Extrae la siguiente información de esta Constancia de Situación Fiscal mexicana (CSF). "
                    "Responde SOLO en formato JSON con estas claves: "
                    '{"rfc": "...", "razon_social": "...", "codigo_postal": "...", '
                    '"regimen_fiscal": "...", "direccion": "..."}. '
                    "Si no encuentras algún dato, usa null."
                )
                llm_response = await llm.chat(user_message=prompt, max_tokens=300, temperature=0.0)
                import json
                import re
                json_match = re.search(r"\{.*\}", llm_response, re.DOTALL)
                if json_match:
                    extracted = json.loads(json_match.group(0))
                    fd.rfc = extracted.get("rfc") or fd.rfc
                    fd.razon_social = extracted.get("razon_social") or fd.razon_social
                    fd.codigo_postal = extracted.get("codigo_postal") or fd.codigo_postal
                    fd.regimen_fiscal = extracted.get("regimen_fiscal") or fd.regimen_fiscal
                    fd.direccion = extracted.get("direccion") or fd.direccion
                    await self.db.commit()
                    return {"success": True, "message": "CSF procesada. Datos extraídos.", "data": extracted}
        except Exception as e:
            logger.error(f"CSF extraction failed: {e}")

        await self.db.commit()
        return {"success": True, "message": "CSF guardada. Usa /api/fiscal/data para completar los datos manualmente."}

    async def get_deduction_recommendations(self, user_id: str) -> Dict:
        """Get deduction recommendations based on the user's fiscal regime."""
        fiscal = await self.get_fiscal_data(user_id)
        if not fiscal or not fiscal.get("regimen_fiscal"):
            return {"message": "Configura tus datos fiscales primero (RFC, régimen, etc.)"}

        regimen = fiscal["regimen_fiscal"]
        rules = REGIME_DEDUCTIONS.get(regimen, {"allowed": ["Gastos en general"], "max_deductions": "Consulta a tu contador"})

        return {
            "regimen": regimen,
            "max_deductions": rules["max_deductions"],
            "allowed_deductions": rules["allowed"],
            "rfc": fiscal.get("rfc"),
            "razon_social": fiscal.get("razon_social"),
        }