"""Iztack-Finance - Credential Manager con almacenamiento en DB."""
import logging
import secrets
import string
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.database.models import StoreCredential, User
from app.utils.crypto import CryptoUtil

logger = logging.getLogger(__name__)


def generate_password(length: int = 16) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


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
                StoreCredential.is_active == True,
            )
            .first()
        )

    async def save_credentials(
        self, user_id: str, store_name: str, username: str, password: str,
        portal_url: str = None, store_category: str = None,
    ) -> StoreCredential:
        """Encrypt and save credentials for a store."""
        encrypted_user = CryptoUtil.encrypt(username, context=f"cred_{user_id}_{store_name}")
        encrypted_pass = CryptoUtil.encrypt(password, context=f"cred_{user_id}_{store_name}")

        cred = StoreCredential(
            user_id=user_id,
            store_name=store_name,
            store_category=store_category or "other",
            portal_url=portal_url,
            encrypted_username=encrypted_user["ciphertext"],
            encrypted_password=encrypted_pass["ciphertext"],
            encryption_key_id=encrypted_user["key_id"],
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
        password = generate_password()
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
            return CryptoUtil.decrypt(
                cred.encrypted_password,
                cred.encryption_key_id,
                context=f"cred_{cred.user_id}_{cred.store_name}",
            )
        except Exception as e:
            logger.error(f"Failed to decrypt password: {e}")
            return None

    async def list_user_credentials(self, user_id: str) -> list:
        """List all stores with saved credentials for a user."""
        creds = (
            self.db.query(StoreCredential)
            .filter(StoreCredential.user_id == user_id, StoreCredential.is_active == True)
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