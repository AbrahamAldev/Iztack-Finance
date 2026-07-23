"""
Iztack-Finance - Tickets Routes
API endpoints for ticket upload and processing.
"""
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import User
from app.modules.auth.deps import get_current_user
from app.modules.tickets.repository import TicketRepository
from app.modules.tickets.service import TicketsService
from app.modules.tickets.tracer import trace_step

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.post("/upload")
async def upload_ticket(
    files: List[UploadFile] = File(...),
    is_continuation: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload one or more ticket images.

    - files: one or more image files (JPEG, PNG, WEBP)
    - is_continuation: if true, images will be stitched together

    Returns OCR results from processed image(s) and persists the ticket in DB.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No se recibieron archivos")

    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Máximo 5 imágenes por ticket")

    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    image_bytes_list = []

    for file in files:
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Formato no soportado: {file.content_type}. Usa JPEG, PNG o WEBP.",
            )

        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"Imagen {file.filename} es demasiado grande. Máximo 10MB.",
            )
        image_bytes_list.append(contents)

    service = TicketsService()
    results = await service.upload_and_process(
        images=image_bytes_list,
        is_continuation=is_continuation,
        user_id=current_user.id,
    )

    saved_tickets = []
    errors = []

    for idx, result in enumerate(results):
        if result.success and result.data:
            try:
                ticket = await TicketRepository.save_ocr_result(
                    db=db,
                    ocr_data=result.data,
                    user_id=current_user.id,
                )
                trace_step(
                    user_id=current_user.id,
                    step="db_save",
                    status="ok",
                    ticket_id=ticket.id,
                    details={"store_name": result.data.store_name, "total_amount": result.data.total_amount},
                )
                saved_tickets.append({
                    "ticket_id": ticket.id,
                    "data": result.data.dict(),
                })
            except Exception as exc:
                trace_step(
                    user_id=current_user.id,
                    step="db_save",
                    status="error",
                    details={"image_index": idx + 1, "error": str(exc)[:500]},
                )
                errors.append(str(exc)[:500])
                raise
        elif result.success:
            saved_tickets.append({"ticket_id": None, "data": None, "message": "OCR procesado pero no se extrajo información estructurada"})
        else:
            errors.append(result.error or f"No se pudo procesar la imagen {idx + 1}")

    if saved_tickets:
        return {
            "success": True,
            "tickets": saved_tickets,
            "count": len(saved_tickets),
            "message": (
                f"{len(saved_tickets)} ticket(s) procesado(s) y guardado(s) correctamente"
                if len(saved_tickets) > 1
                else "Ticket procesado y guardado correctamente"
            ),
            "errors": errors if errors else None,
        }

    return {
        "success": False,
        "error": errors[0] if errors else "No se pudo procesar el ticket",
        "suggestion": "Asegúrate de que la foto sea clara y esté bien iluminada",
    }


@router.post("/upload-base64")
async def upload_ticket_base64(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload ticket image(s) as base64 strings.

    Body: {
        "images": ["base64_string_1", "base64_string_2"],
        "is_continuation": true
    }
    """
    import base64

    images_base64 = data.get("images", [])
    is_continuation = data.get("is_continuation", False)

    if not images_base64:
        raise HTTPException(status_code=400, detail="No se recibieron imágenes")

    if len(images_base64) > 5:
        raise HTTPException(status_code=400, detail="Máximo 5 imágenes por ticket")

    image_bytes_list = []
    for b64_str in images_base64:
        try:
            # Remove data URL prefix if present
            if "," in b64_str:
                b64_str = b64_str.split(",")[1]
            image_bytes = base64.b64decode(b64_str)
            if len(image_bytes) > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=400, detail="Imagen demasiado grande. Máximo 10MB."
                )
            image_bytes_list.append(image_bytes)
        except Exception:
            raise HTTPException(
                status_code=400, detail="Base64 inválido en una de las imágenes"
            )

    service = TicketsService()
    results = await service.upload_and_process(
        images=image_bytes_list,
        is_continuation=is_continuation,
        user_id=current_user.id,
    )

    saved_tickets = []
    errors = []

    for idx, result in enumerate(results):
        if result.success and result.data:
            try:
                ticket = await TicketRepository.save_ocr_result(
                    db=db,
                    ocr_data=result.data,
                    user_id=current_user.id,
                )
                trace_step(
                    user_id=current_user.id,
                    step="db_save",
                    status="ok",
                    ticket_id=ticket.id,
                    details={"store_name": result.data.store_name, "total_amount": result.data.total_amount},
                )
                saved_tickets.append({
                    "ticket_id": ticket.id,
                    "data": result.data.dict(),
                })
            except Exception as exc:
                trace_step(
                    user_id=current_user.id,
                    step="db_save",
                    status="error",
                    details={"image_index": idx + 1, "error": str(exc)[:500]},
                )
                errors.append(str(exc)[:500])
                raise
        elif result.success:
            saved_tickets.append({"ticket_id": None, "data": None, "message": "OCR procesado pero no se extrajo información estructurada"})
        else:
            errors.append(result.error or f"No se pudo procesar la imagen {idx + 1}")

    if saved_tickets:
        return {
            "success": True,
            "tickets": saved_tickets,
            "count": len(saved_tickets),
            "message": (
                f"{len(saved_tickets)} ticket(s) procesado(s) y guardado(s) correctamente"
                if len(saved_tickets) > 1
                else "Ticket procesado y guardado correctamente"
            ),
            "errors": errors if errors else None,
        }

    return {
        "success": False,
        "error": errors[0] if errors else "No se pudo procesar el ticket",
    }
