"""
Iztack-Finance - Chat Routes
API endpoints for in-app chat messaging.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import ProcessingError, User
from app.modules.auth.deps import get_current_user
from app.modules.chat.service import ChatService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/report")
async def submit_report(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a bug report from the chat widget."""
    try:
        error = ProcessingError(
            user_id=current_user.id,
            error_type="user_report",
            error_message=f"Reporte de {current_user.name} ({current_user.email}): {data.get('message', 'Sin mensaje')}",
            error_details=data,
            suggested_action="Revisar en admin portal",
        )
        db.add(error)
        await db.commit()
        return {"success": True, "message": "Reporte enviado"}
    except Exception as e:
        logger.error(f"Error saving report: {e}")
        raise HTTPException(status_code=500, detail="No se pudo guardar el reporte")



@router.post("/message")
async def send_message(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a chat message (text and/or image).
    Returns AI-generated response.
    """
    image_bytes = None
    if file:
        allowed_types = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Formato no soportado: {file.content_type}. Usa JPEG, PNG o WEBP.",
            )
        image_bytes = await file.read()
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Imagen demasiado grande. Máximo 10MB.")

    if not text and not image_bytes:
        raise HTTPException(status_code=400, detail="Envía un mensaje o una imagen.")

    service = ChatService(db)
    response_text, metadata = await service.process_message(
        user_id=current_user.id,
        text=text,
        image_bytes=image_bytes,
    )

    return {
        "response": response_text,
        "metadata": metadata,
    }


@router.get("/history")
async def get_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get chat history for the current user."""
    service = ChatService(db)
    messages = await service.get_history(current_user.id, limit=limit)
    return {"messages": messages}
