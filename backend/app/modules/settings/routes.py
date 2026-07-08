"""
Iztack-Finance - Settings Routes
API endpoints for user settings (Telegram, Google Drive).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.modules.auth.deps import get_current_user
from app.modules.settings.service import SettingsService
from app.database.models import User

router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.get("")
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user settings."""
    try:
        settings = await SettingsService(db).get_settings(current_user.id)
        return settings
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/telegram")
async def update_telegram(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update Telegram chat_id for the user."""
    chat_id = data.get("chat_id", "")
    if not chat_id:
        raise HTTPException(status_code=400, detail="chat_id requerido")

    try:
        user = await SettingsService(db).update_telegram_chat_id(
            current_user.id, chat_id
        )
        return {
            "success": True,
            "telegram_configured": bool(user.telegram_chat_id),
            "message": "Chat ID de Telegram actualizado",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/google-drive")
async def update_google_drive(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update Google Drive credentials for the user."""
    refresh_token = data.get("refresh_token", "")
    folder_id = data.get("folder_id", "")

    if not refresh_token or not folder_id:
        raise HTTPException(
            status_code=400,
            detail="refresh_token y folder_id requeridos",
        )

    try:
        user = await SettingsService(db).update_google_drive(
            current_user.id, refresh_token, folder_id
        )
        return {
            "success": True,
            "google_drive_configured": True,
            "message": "Credenciales de Google Drive actualizadas",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/google-drive/status")
async def google_drive_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get Google Drive storage status for the user."""
    try:
        status = await SettingsService(db).get_google_drive_status(current_user.id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))