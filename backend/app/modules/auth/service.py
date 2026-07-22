"""
Iztack-Finance - Auth Service
Business logic for user registration, login, and JWT token management.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
import secrets
import string
import hashlib

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, Tenant
from app.modules.auth.schemas import (
    RegisterRequest, LoginRequest, UserUpdateRequest,
    UserResponse, TokenResponse
)
from app.utils.hashing import PasswordHasher
from app.config import get_settings

logger = logging.getLogger(__name__)

# JWT configuration — derived from app settings so it persists across restarts
_settings = get_settings()
JWT_SECRET = _settings.secret_key
JWT_ALGORITHM = _settings.algorithm
JWT_EXPIRE_HOURS = _settings.access_token_expire_minutes / 60


class AuthService:
    """Authentication service for user management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: RegisterRequest) -> Tuple[User, str]:
        """
        Register a new user.
        Creates a tenant if tenant_name provided, otherwise uses a default.
        Returns (user, access_token).
        """
        # Check if email already exists
        existing = await self._get_user_by_email(data.email)
        if existing:
            raise ValueError("El email ya está registrado")

        # Create or get tenant
        tenant_id = await self._get_or_create_tenant(data.tenant_name or f"Tenant de {data.name}")

        # Hash password
        password_hash = PasswordHasher.hash_password(data.password)

        # Create user
        user = User(
            email=data.email.lower().strip(),
            name=data.name.strip(),
            password_hash=password_hash,
            tenant_id=tenant_id,
            is_active=True,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Generate token
        token = self._generate_token(user.id, user.tenant_id)

        logger.info(f"User registered: {user.email} (tenant={tenant_id})")
        return user, token

    async def login(self, data: LoginRequest) -> Tuple[User, str]:
        """Authenticate user and return token."""
        user = await self._get_user_by_email(data.email)
        if not user:
            raise ValueError("Credenciales inválidas")

        if not user.is_active:
            raise ValueError("Cuenta desactivada")

        if not PasswordHasher.verify_password(data.password, user.password_hash):
            raise ValueError("Credenciales inválidas")

        # Update last login
        user.last_login_at = datetime.utcnow()
        await self.db.commit()

        token = self._generate_token(user.id, user.tenant_id)
        logger.info(f"User logged in: {user.email}")
        return user, token

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_user(self, user_id: str, data: UserUpdateRequest) -> User:
        """Update user profile."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        if data.name is not None:
            user.name = data.name.strip()
        if data.timezone is not None:
            user.timezone = data.timezone
        if data.currency is not None:
            user.currency = data.currency
        if data.telegram_chat_id is not None:
            user.telegram_chat_id = data.telegram_chat_id.strip() or None

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> bool:
        """Change user password."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        if not PasswordHasher.verify_password(current_password, user.password_hash):
            raise ValueError("Contraseña actual incorrecta")

        user.password_hash = PasswordHasher.hash_password(new_password)
        await self.db.commit()
        return True

    # --- Private helpers ---

    async def _get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def _get_or_create_tenant(self, tenant_name: str) -> str:
        """Get or create a tenant by name."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.name == tenant_name.strip())
        )
        tenant = result.scalar_one_or_none()
        if tenant:
            return tenant.id

        tenant = Tenant(name=tenant_name.strip())
        self.db.add(tenant)
        await self.db.commit()
        await self.db.refresh(tenant)
        return tenant.id

    def _generate_token(self, user_id: str, tenant_id: Optional[str]) -> str:
        """Generate a JWT token (simplified, no external deps)."""
        import base64
        import json

        header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
        payload = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)).timestamp()),
        }

        # Base64url encode
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")

        # Signature (HMAC-SHA256)
        import hmac
        signature = hmac.new(
            JWT_SECRET.encode(),
            f"{header_b64}.{payload_b64}".encode(),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

        return f"{header_b64}.{payload_b64}.{signature_b64}"

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify JWT token and return payload."""
        import base64
        import json
        import hmac
        import hashlib

        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_b64, payload_b64, signature_b64 = parts

            # Verify signature
            expected_sig = hmac.new(
                JWT_SECRET.encode(),
                f"{header_b64}.{payload_b64}".encode(),
                hashlib.sha256
            ).digest()
            expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")

            if not hmac.compare_digest(signature_b64, expected_sig_b64):
                return None

            # Decode payload
            padding = "=" * (4 - len(payload_b64) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_b64 + padding))

            # Check expiration
            if payload.get("exp", 0) < datetime.utcnow().timestamp():
                return None

            return payload
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None