"""
Iztack-Finance - Tickets Routes
API endpoints for ticket upload and processing.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.modules.auth.deps import get_current_user
from app.modules.tickets.service import TicketsService
from app.database.models import User

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.post("/upload")
async def upload_ticket(
    files: List[UploadFile] = File(...),
    is_continuation: bool = Form(False),
    current_user: User = Depends(get_current_user),
):
    """
    Upload one or more ticket images.
    
    - files: one or more image files (JPEG, PNG, WEBP)
    - is_continuation: if true, images will be stitched together
    
    Returns OCR results from processed image(s).
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
    result = await service.upload_and_process(
        images=image_bytes_list,
        is_continuation=is_continuation,
        user_id=current_user.id,
    )

    if result.success:
        return {
            "success": True,
            "data": result.data.dict() if result.data else None,
            "message": "Ticket procesado correctamente"
            if len(image_bytes_list) == 1
            else f"{len(image_bytes_list)} imágenes combinadas correctamente",
        }
    else:
        return {
            "success": False,
            "error": result.error or "No se pudo procesar el ticket",
            "suggestion": "Asegúrate de que la foto sea clara y esté bien iluminada",
        }


@router.post("/upload-base64")
async def upload_ticket_base64(
    data: dict,
    current_user: User = Depends(get_current_user),
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
    result = await service.upload_and_process(
        images=image_bytes_list,
        is_continuation=is_continuation,
        user_id=current_user.id,
    )

    if result.success:
        return {
            "success": True,
            "data": result.data.dict() if result.data else None,
            "message": "Ticket procesado correctamente",
        }
    else:
        return {
            "success": False,
            "error": result.error or "No se pudo procesar el ticket",
        }