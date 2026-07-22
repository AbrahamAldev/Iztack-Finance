"""
Validator Agent — validates OCR output for consistency and quality.
"""
import logging
from datetime import date
from app.agents.base import Agent, AgentContext, AgentResult
from app.modules.ocr.schemas import OCRTicketData

logger = logging.getLogger(__name__)


class ValidatorAgent(Agent):
    """Agent specialized in validating extracted ticket data."""

    name = "validator"
    description = "Valida coherencia de datos extraídos por OCR."

    SYSTEM_PROMPT = """Eres un validador de datos de tickets de compra mexicanos.

Recibirás un JSON con datos extraídos por OCR. Tu tarea es:
1. Verificar que el total sea coherente (si hay subtotal + impuestos, debe coincidir aproximadamente).
2. Verificar que la fecha sea válida y no futura.
3. Verificar que haya al menos un producto o un total mayor a 0.
4. Detectar posibles duplicados o datos sospechosos.

Responde ÚNICAMENTE en formato JSON:
{
  "valid": true|false,
  "confidence": 0.0-1.0,
  "issues": ["descripción del problema 1", "problema 2"],
  "suggested_action": "mensaje para el usuario si hay problema"
}

Si todo está bien, issues debe ser una lista vacía."""

    async def run(self, context: AgentContext) -> AgentResult:
        data = context.payload.get("ocr_data")
        if not data:
            return self.fail("No se proporcionaron datos OCR para validar")

        # Programmatic pre-validation
        issues = []
        try:
            ticket = OCRTicketData(**data) if isinstance(data, dict) else data
        except Exception as e:
            return self.fail(f"Datos OCR inválidos: {e}")

        if not ticket.store_name:
            issues.append("No se detectó el nombre de la tienda")

        if ticket.total_amount is None or ticket.total_amount <= 0:
            issues.append("El total no es válido")

        if ticket.purchase_date and ticket.purchase_date > date.today():
            issues.append("La fecha de compra es futura")

        if ticket.subtotal is not None and ticket.taxes is not None:
            expected = round(ticket.subtotal + ticket.taxes, 2)
            actual = round(ticket.total_amount or 0, 2)
            if abs(expected - actual) > 1.0:
                issues.append(f"El total ({actual}) no coincide con subtotal + impuestos ({expected})")

        if ticket.confidence < 0.4:
            issues.append("La confianza del OCR es baja")

        # LLM validation for nuanced checks
        llm_validation = await self._llm_validate(ticket)
        issues.extend(llm_validation.get("issues", []))

        is_valid = len(issues) == 0
        return self.ok(
            output={
                "valid": is_valid,
                "issues": issues,
                "confidence": ticket.confidence,
                "llm_validation": llm_validation,
            },
            metadata={"requires_user_input": not is_valid},
        )

    async def _llm_validate(self, ticket: OCRTicketData) -> dict:
        """Ask LLM for additional validation."""
        try:
            prompt = f"Datos extraídos del ticket:\n{ticket.model_dump_json(indent=2)}"
            response = await self.call_llm(
                system_prompt=self.SYSTEM_PROMPT,
                user_message=prompt,
                temperature=0.0,
                max_tokens=512,
            )
            import json, re
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception as e:
            logger.warning(f"LLM validation failed: {e}")
        return {"valid": True, "issues": [], "confidence": 1.0}
