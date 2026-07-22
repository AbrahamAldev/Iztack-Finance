"""
OCR Agent — extracts structured ticket data from images.

This agent wraps the existing OCRService for backward compatibility
while adding agent-specific tracing and error handling.
"""
import logging
from typing import Optional

from app.agents.base import Agent, AgentContext, AgentResult
from app.modules.ocr.service import OCRService
from app.modules.ocr.schemas import OCRResponse
from app.modules.tickets.tracer import trace_step

logger = logging.getLogger(__name__)


class OCRAgent(Agent):
    """Agent specialized in extracting data from receipt images."""

    name = "ocr"
    description = "Extrae datos estructurados de tickets de compra."

    def __init__(self, llm_client, config=None):
        super().__init__(llm_client, config)
        self.ocr_service = OCRService()

    async def run(self, context: AgentContext) -> AgentResult:
        image_bytes = context.payload.get("image_bytes")
        if not image_bytes:
            return self.fail("No se proporcionó imagen para OCR")

        user_id = context.user_id or "anonymous"
        trace_step(user_id, "ocr_agent_start", status="ok", details={"size_bytes": len(image_bytes)})

        try:
            result: OCRResponse = self.ocr_service.extract_from_image(image_bytes)
            trace_step(
                user_id,
                "ocr_agent_end",
                status="ok" if result.success else "error",
                details={
                    "success": result.success,
                    "store_name": result.data.store_name if result.data else None,
                    "confidence": result.data.confidence if result.data else None,
                },
            )

            if result.success and result.data:
                return self.ok(
                    output=result.data,
                    metadata={"raw_text": result.raw_text, "confidence": result.data.confidence},
                )
            return self.fail(result.error or "OCR no pudo extraer datos del ticket")
        except Exception as e:
            logger.error(f"OCRAgent error: {e}", exc_info=True)
            trace_step(user_id, "ocr_agent_end", status="error", details={"error": str(e)})
            return self.fail(f"Error en OCR: {str(e)}")
