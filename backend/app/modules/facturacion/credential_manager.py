"""Iztack-Finance - Credential Manager con almacenamiento en DB."""
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.database.models import StoreCredential
from app.utils.crypto import CryptoManager

logger = logging.getLogger(__name__)

crypto = CryptoManager()


class CredentialManager:
    """Manages store credentials with encryption at rest."""

    def __init__(self, db: Session):
        self.db = db

    async def get_credentials(self, user_id: str, store_name: str) -> Optional[StoreCredential]:
        """Get stored credentials for a user and store."""
        return (
            self.db.query(StoreCredential)
            .filter(
                StoreCredential.user_id == user_id,
                StoreCredential.store_name.ilike(f"%{store_name}%"),
                StoreCredential.is_active.is_(True),
            )
            .first()
        )

    async def save_credentials(
        self, user_id: str, store_name: str, username: str, password: str,
        portal_url: str = None, store_category: str = None,
    ) -> StoreCredential:
        """Encrypt and save credentials for a store."""
        context = f"cred_{user_id}_{store_name}"
        encrypted_user = crypto.encrypt_to_blob(username, context=context)
        encrypted_pass = crypto.encrypt_to_blob(password, context=context)

        cred = StoreCredential(
            user_id=user_id,
            store_name=store_name,
            store_category=store_category or "other",
            portal_url=portal_url,
            encrypted_username=encrypted_user,
            encrypted_password=encrypted_pass,
            encryption_key_id="blob",
            credential_hint=username,
            email_registered=username,
            has_account=True,
            account_created_automatically=False,
            is_active=True,
        )
        self.db.add(cred)
        self.db.commit()
        self.db.refresh(cred)
        logger.info(f"Credentials saved for {store_name} (user {user_id})")
        return cred

    async def create_account(
        self, user_id: str, store_name: str, email: str, portal_url: str = None,
    ) -> StoreCredential:
        """Create a new account for a store and save credentials."""
        password = crypto.generate_password()
        return await self.save_credentials(
            user_id=user_id,
            store_name=store_name,
            username=email,
            password=password,
            portal_url=portal_url,
        )

    async def get_decrypted_password(self, cred: StoreCredential) -> Optional[str]:
        """Decrypt a stored password."""
        try:
            return crypto.decrypt_from_blob(
                cred.encrypted_password,
                context=f"cred_{cred.user_id}_{cred.store_name}",
            )
        except Exception as e:
            logger.error(f"Failed to decrypt password: {e}")
            return None

    async def get_decrypted_username(self, cred: StoreCredential) -> Optional[str]:
        """Decrypt a stored username."""
        try:
            return crypto.decrypt_from_blob(
                cred.encrypted_username,
                context=f"cred_{cred.user_id}_{cred.store_name}",
            )
        except Exception as e:
            logger.error(f"Failed to decrypt username: {e}")
            return None

    async def list_user_credentials(self, user_id: str) -> list:
        """List all stores with saved credentials for a user."""
        creds = (
            self.db.query(StoreCredential)
            .filter(StoreCredential.user_id == user_id, StoreCredential.is_active.is_(True))
            .all()
        )
        return [
            {
                "store_name": c.store_name,
                "username": c.credential_hint,
                "has_account": c.has_account,
                "last_used": c.last_used_at.isoformat() if c.last_used_at else None,
            }
            for c in creds
        ]
