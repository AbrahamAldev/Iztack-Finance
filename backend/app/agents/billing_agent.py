"""
Billing Agent — decides and executes CFDI invoicing workflows.

Wraps the existing FacturacionOrchestrator for gradual migration.
"""
import logging
import os

from app.agents.base import Agent, AgentContext, AgentResult
from app.modules.tickets.billing import trigger_billing

logger = logging.getLogger(__name__)


class BillingAgent(Agent):
    """Agent specialized in automatic CFDI invoicing."""

    name = "billing"
    description = "Gestiona la facturación automática CFDI post-OCR."

    SYSTEM_PROMPT = """Eres el agente de facturación de Iztack-Finance.

Tu trabajo es decidir si un ticket requiere facturación CFDI y, en su caso,
preparar la información necesaria para el orquestador de facturación.

REGLAS:
1. Solo factura si el usuario lo solicita o si hay una política configurada.
2. Identifica la tienda y busca si existe un portal de facturación conocido.
3. Verifica que la fecha de compra esté dentro del plazo permitido.
4. Si faltan datos fiscales del usuario, solicítalos.

Responde ÚNICAMENTE en formato JSON:
{
  "should_invoice": true|false,
  "reason": "breve explicación",
  "store_name": "nombre de tienda",
  "missing_data": ["rfc", "regimen_fiscal", ...]
}
"""

    async def run(self, context: AgentContext) -> AgentResult:
        ocr_data = context.payload.get("ocr_data")
        user_id = context.user_id
        db_session = context.payload.get("db_session")

        if not ocr_data or not user_id:
            return self.fail("Faltan datos OCR o user_id para facturación")

        # Quick decision via LLM
        prompt = f"""Datos del ticket:\n{ocr_data}

¿Deberíamos intentar facturar este ticket automáticamente?"""
        response = await self.call_llm(
            system_prompt=self.SYSTEM_PROMPT,
            user_message=prompt,
            temperature=0.1,
            max_tokens=512,
        )

        import json
        import re
        decision = {"should_invoice": False, "reason": "No se pudo decidir"}
        try:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                decision = json.loads(match.group(0))
        except Exception as e:
            logger.warning(f"Billing decision parse failed: {e}")

        if not decision.get("should_invoice"):
            return self.ok(
                output={"invoiced": False, "reason": decision.get("reason")},
            )

        # Trigger existing orchestrator if API key is available
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key or not db_session:
            return self.ok(
                output={"invoiced": False, "reason": "Falta API key o sesión de DB"},
                requires_user_input=True,
                user_message="La facturación automática requiere configuración adicional.",
            )

        try:
            ctx = await trigger_billing(ocr_data, user_id, db_session)
            return self.ok(
                output={
                    "invoiced": ctx.step.value == "completed" if ctx else False,
                    "step": ctx.step.value if ctx else None,
                    "needs_user_input": ctx.needs_user_input if ctx else False,
                    "user_message": ctx.user_message if ctx else None,
                },
                requires_user_input=ctx.needs_user_input if ctx else False,
                user_message=ctx.user_message if ctx else None,
            )
        except Exception as e:
            logger.error(f"BillingAgent error: {e}", exc_info=True)
            return self.fail(f"Error al facturar: {str(e)}")
