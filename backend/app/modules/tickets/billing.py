"""Iztack-Finance - Post-OCR Billing Trigger. Dispara facturación automática tras procesar un ticket."""
import logging
from typing import Optional, Dict, Any

from app.database.models import Ticket, User
from app.utils.llm import LLMClient
from app.modules.facturacion.orchestrator import FacturacionOrchestrator, InvoiceContext
from app.modules.ocr.schemas import OCRTicketData

logger = logging.getLogger(__name__)


async def trigger_billing(
    ocr_data: OCRTicketData, user: User, db_session
) -> Optional[InvoiceContext]:
    """Trigger automatic billing after successful OCR."""
    if not ocr_data.store_name:
        logger.warning("No store name in OCR data, skipping billing")
        return None

    # Create or update ticket record
    ticket = Ticket(
        user_id=user.id,
        store_name=ocr_data.store_name,
        store_category=ocr_data.store_category,
        purchase_date=ocr_data.purchase_date,
        total_amount=ocr_data.total_amount or 0,
        status="ocr_completed",
        ocr_raw_text=getattr(ocr_data, "raw_text", ""),
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    # Initialize orchestrator and start billing
    api_key = __import__("os").environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        logger.warning("No OPENROUTER_API_KEY, skipping billing orchestration")
        return None

    llm_client = LLMClient(api_key)
    orchestrator = FacturacionOrchestrator(llm_client)
    
    ctx = await orchestrator.start_invoicing(ticket, user)
    
    if ctx.needs_user_input and ctx.user_message:
        logger.info(f"Billing needs user input: {ctx.step.value}")
    
    return ctx