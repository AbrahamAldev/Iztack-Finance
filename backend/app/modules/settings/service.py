"""
Iztack-Finance - Settings Service
User-specific settings: Telegram chat_id, Google Drive credentials.
"""
import logging
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.modules.auth.service import AuthService
from app.utils.crypto import CryptoManager

logger = logging.getLogger(__name__)


class SettingsService:
    """Manage user settings (Telegram, Google Drive)."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.crypto = CryptoManager()

    async def update_telegram_chat_id(self, user_id: str, chat_id: str) -> User:
        """Update user's Telegram chat_id."""
        user = await AuthService(self.db).get_user_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        user.telegram_chat_id = chat_id.strip() or None
        await self.db.commit()
        await self.db.refresh(user)
        logger.info(f"Telegram chat_id updated for user {user_id}")
        return user

    async def update_google_drive(
        self, user_id: str, refresh_token: str, folder_id: str
    ) -> User:
        """Update user's Google Drive credentials (encrypted)."""
        user = await AuthService(self.db).get_user_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        # Encrypt credentials (returns ciphertext, nonce, key_id)
        enc_refresh, nonce_refresh, key_id = self.crypto.encrypt(refresh_token)
        enc_folder, nonce_folder, _ = self.crypto.encrypt(folder_id)

        # Store as: ciphertext + nonce (combined for storage)
        import base64
        user.encrypted_google_refresh_token = base64.b64encode(enc_refresh + nonce_refresh)
        user.encrypted_google_drive_folder_id = base64.b64encode(enc_folder + nonce_folder)
        user.encryption_key_id = key_id

        await self.db.commit()
        await self.db.refresh(user)
        logger.info(f"Google Drive credentials updated for user {user_id}")
        return user

    async def get_google_drive_status(self, user_id: str) -> dict:
        """
        Get Google Drive storage quota for the user.
        Returns dict with used_bytes, total_bytes, percentage.
        """
        user = await AuthService(self.db).get_user_by_id(user_id)
        if not user or not user.encrypted_google_refresh_token:
            return {"configured": False}

        # TODO: Call Google Drive API to get quota
        # For now return placeholder
        return {
            "configured": True,
            "used_bytes": 0,
            "total_bytes": 15 * 1024 * 1024 * 1024 * 1024,  # 15 TB placeholder
            "percentage": 0.0,
            "warning": False,
        }

    async def get_settings(self, user_id: str) -> dict:
        """Get all user settings (non-sensitive)."""
        user = await AuthService(self.db).get_user_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        return {
            "telegram_configured": bool(user.telegram_chat_id),
            "google_drive_configured": bool(user.encrypted_google_refresh_token),
            "name": user.name,
            "email": user.email,
            "timezone": user.timezone,
            "currency": user.currency,
        }