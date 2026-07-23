"""
Iztack-Finance - Storage Routes
API endpoints for invoice/document storage (Google Drive/local).
"""
import base64
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import User
from app.modules.almacenamiento.drive_service import DriveStorageService
from app.modules.almacenamiento.local_storage import LocalStorageService
from app.modules.auth.deps import get_current_user
from app.modules.tickets.tracer import trace_step

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/almacenamiento", tags=["Almacenamiento"])


@router.post("/invoices")
async def store_invoice(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Store an invoice PDF/XML in Google Drive.

    Body:
    {
        "store_name": "Liverpool",
        "purchase_date": "2026-07-22",
        "ticket_id": "uuid",
        "pdf_base64": "...",
        "xml_base64": "...",
        "has_warranty": false,
        "expense_type": "electronicos"
    }
    """
    from datetime import date as dt_date

    store_name = data.get("store_name")
    purchase_date_str = data.get("purchase_date")
    ticket_id = data.get("ticket_id")
    pdf_base64 = data.get("pdf_base64")
    xml_base64 = data.get("xml_base64")

    if not store_name or not purchase_date_str or not ticket_id:
        raise HTTPException(status_code=400, detail="Faltan store_name, purchase_date o ticket_id")

    try:
        purchase_date = dt_date.fromisoformat(purchase_date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="purchase_date inválida (YYYY-MM-DD)")

    pdf_bytes = None
    xml_bytes = None
    try:
        if pdf_base64:
            pdf_bytes = base64.b64decode(pdf_base64)
        if xml_base64:
            xml_bytes = base64.b64decode(xml_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="pdf_base64 o xml_base64 inválido")

    if not pdf_bytes and not xml_bytes:
        raise HTTPException(status_code=400, detail="Se requiere pdf_base64 o xml_base64")

    try:
        drive = DriveStorageService()
        result = await drive.save_invoice(
            store_name=store_name,
            purchase_date=purchase_date,
            pdf_bytes=pdf_bytes,
            xml_bytes=xml_bytes,
            ticket_id=ticket_id,
            has_warranty=data.get("has_warranty", False),
            expense_type=data.get("expense_type", ""),
        )
        local = LocalStorageService(current_user.id)
        local.save_invoice_file(
            invoice_id=ticket_id,
            pdf_bytes=pdf_bytes,
            xml_bytes=xml_bytes,
        )
        trace_step(
            user_id=current_user.id,
            step="storage_invoice_save",
            status="ok",
            ticket_id=ticket_id,
            details={"store_name": store_name, "drive_urls": result},
        )
        return {"success": True, "drive_urls": result}
    except Exception as exc:
        logger.error(f"Error storing invoice: {exc}", exc_info=True)
        trace_step(
            user_id=current_user.id,
            step="storage_invoice_save",
            status="error",
            ticket_id=ticket_id,
            details={"error": str(exc)[:500]},
        )
        raise HTTPException(status_code=500, detail="No se pudo guardar en Drive")


@router.get("/invoices")
async def list_invoices(
    folder: str = "por_establecimiento",
    store: str = "",
    year: int = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List invoices stored in Google Drive."""
    try:
        drive = DriveStorageService()
        files = await drive.list_invoices(folder_key=folder, store_name=store, year=year)
        trace_step(
            user_id=current_user.id,
            step="storage_invoice_list",
            status="ok",
            details={"folder": folder, "count": len(files)},
        )
        return {"folder": folder, "files": files, "count": len(files)}
    except Exception as exc:
        logger.error(f"Error listing invoices: {exc}", exc_info=True)
        trace_step(
            user_id=current_user.id,
            step="storage_invoice_list",
            status="error",
            details={"error": str(exc)[:500]},
        )
        raise HTTPException(status_code=500, detail="No se pudo listar archivos de Drive")
