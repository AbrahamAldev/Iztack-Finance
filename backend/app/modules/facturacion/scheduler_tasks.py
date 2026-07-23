"""
Iztack-Finance - Facturación Scheduler Tasks
Background processing of pending invoices using APScheduler.
"""
import logging
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import async_session
from app.database.models import InvoiceStatus, Ticket
from app.modules.facturacion.orchestrator import FacturacionOrchestrator
from app.utils.llm import get_llm_client

logger = logging.getLogger(__name__)


async def process_pending_invoices() -> dict:
    """
    Poll for tickets with pending invoices and start the billing workflow.
    Runs as an APScheduler job.
    """
    db: AsyncSession = async_session()
    try:
        cutoff = date.today() - timedelta(days=60)
        result = await db.execute(
            select(Ticket).where(
                Ticket.invoice_status == InvoiceStatus.PENDING.value,
                Ticket.purchase_date >= cutoff,
                Ticket.status.notin_(["error", "duplicated"]),
            ).order_by(Ticket.created_at.asc()).limit(10)
        )
        tickets = result.scalars().all()

        if not tickets:
            return {"processed": 0, "message": "No pending invoices"}

        llm = get_llm_client()
        if not llm:
            logger.warning("Skipping invoice processing: no LLM client available")
            return {"processed": 0, "message": "LLM not configured"}

        processed = 0
        errors = 0
        for ticket in tickets:
            try:
                # Load user
                from app.database.models import User
                user_result = await db.execute(
                    select(User).where(User.id == ticket.user_id)
                )
                user = user_result.scalar_one_or_none()
                if not user:
                    logger.warning("No user found for ticket %s", ticket.id)
                    continue

                # Mark as in-progress to avoid duplicate processing
                ticket.invoice_status = InvoiceStatus.REQUESTED.value
                await db.commit()

                orchestrator = FacturacionOrchestrator(llm, db)
                ctx = await orchestrator.start_invoicing(ticket, user)

                if ctx.step.value == "completed":
                    ticket.invoice_status = InvoiceStatus.DOWNLOADED.value
                    processed += 1
                elif ctx.needs_user_input:
                    # Pause and wait for user interaction
                    ticket.invoice_status = InvoiceStatus.PENDING.value
                    logger.info(
                        "Invoice %s waiting for user input: %s",
                        ticket.id,
                        ctx.user_message,
                    )
                else:
                    ticket.invoice_status = InvoiceStatus.ERROR.value
                    ticket.error_message = ctx.error or "Facturación falló"
                    errors += 1

                await db.commit()
            except Exception as exc:
                errors += 1
                logger.exception("Invoice processing failed for ticket %s: %s", ticket.id, exc)
                try:
                    ticket.invoice_status = InvoiceStatus.ERROR.value
                    ticket.error_message = str(exc)[:500]
                    await db.commit()
                except Exception:
                    pass

        return {"processed": processed, "errors": errors, "total": len(tickets)}
    finally:
        await db.close()
