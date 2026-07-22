"""
Iztack-Finance - Admin Staff Service
Authentication and dashboard for admin portal.
"""
import logging
import hashlib
import secrets
import base64
import json
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.database.models import StaffUser, User, Ticket
from app.utils.hashing import PasswordHasher
from app.config import get_settings

logger = logging.getLogger(__name__)

# JWT configuration — derived from app settings so it persists across restarts
_settings = get_settings()
JWT_SECRET = _settings.secret_key
JWT_ALGORITHM = _settings.algorithm
JWT_EXPIRE_HOURS = 8


class AdminStaffService:
    """Admin staff authentication and management."""

    def __init__(self, db: Session):
        self.db = db

    async def login(self, email: str, password: str) -> Tuple[StaffUser, str]:
        """Login staff user. Only @iztack.com emails allowed."""
        email = email.lower().strip()

        if not email.endswith("@iztack.com"):
            raise ValueError("Solo correos @iztack.com pueden acceder al portal admin")

        user = self.db.query(StaffUser).filter(
            StaffUser.email == email,
            StaffUser.is_active == True
        ).first()

        if not user:
            raise ValueError("Credenciales inválidas")

        if not PasswordHasher.verify_password(password, user.password_hash):
            raise ValueError("Credenciales inválidas")

        user.last_login_at = datetime.utcnow()
        self.db.commit()

        token = self._generate_token(user)
        return user, token

    async def register_first_admin(self, email: str, name: str, password: str) -> Tuple[StaffUser, str]:
        """Register the first admin (admin@iztack.com only)."""
        email = email.lower().strip()

        if email != "admin@iztack.com":
            raise ValueError("Solo admin@iztack.com puede ser super_admin inicial")

        existing = self.db.query(StaffUser).filter(StaffUser.email == email).first()
        if existing:
            raise ValueError("El admin ya existe. Usa otro método.")

        password_hash = PasswordHasher.hash_password(password)
        user = StaffUser(
            email=email,
            name=name,
            password_hash=password_hash,
            role="super_admin",
            role_level=100,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        token = self._generate_token(user)
        return user, token

    async def get_health(self) -> dict:
        """Get system health status."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "backend": {"status": "up", "uptime": "running"},
                "database": {"status": "up", "uptime": "connected"},
            }
        }

    async def get_clients_summary(self) -> list:
        """Get list of client users (non-sensitive)."""
        users = self.db.query(User).order_by(User.created_at.desc()).limit(50).all()
        return [
            {
                "id": u.id,
                "email": u.email,
                "name": u.name,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "telegram_linked": bool(u.telegram_chat_id),
                "drive_configured": bool(u.encrypted_google_refresh_token),
            }
            for u in users
        ]

    async def get_staff_users(self) -> list:
        """Get list of staff users."""
        staff = self.db.query(StaffUser).order_by(StaffUser.created_at.desc()).all()
        return [
            {
                "id": s.id,
                "email": s.email,
                "name": s.name,
                "role": s.role,
                "role_level": s.role_level,
                "is_active": s.is_active,
                "last_login": s.last_login_at.isoformat() if s.last_login_at else None,
            }
            for s in staff
        ]

    async def update_staff_role(self, staff_id: str, role: str, role_level: int, current_user: StaffUser) -> StaffUser:
        """Update staff user role (super_admin only)."""
        if current_user.role != "super_admin":
            raise ValueError("Solo super_admin puede cambiar roles")

        target = self.db.query(StaffUser).filter(StaffUser.id == staff_id).first()
        if not target:
            raise ValueError("Staff no encontrado")

        target.role = role
        target.role_level = role_level
        self.db.commit()
        self.db.refresh(target)
        return target

    def _generate_token(self, user: StaffUser) -> str:
        header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
        payload = {
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "role_level": user.role_level,
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)).timestamp()),
        }
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        import hmac
        signature = hmac.new(
            JWT_SECRET.encode(),
            f"{header_b64}.{payload_b64}".encode(),
            hashlib.sha256
        ).digest()
        sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
        return f"{header_b64}.{payload_b64}.{sig_b64}"

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            header_b64, payload_b64, signature_b64 = parts
            import hmac
            expected_sig = hmac.new(
                JWT_SECRET.encode(),
                f"{header_b64}.{payload_b64}".encode(),
                hashlib.sha256
            ).digest()
            expected_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
            if not hmac.compare_digest(signature_b64, expected_b64):
                return None
            padding = "=" * (4 - len(payload_b64) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_b64 + padding))
            if payload.get("exp", 0) < datetime.utcnow().timestamp():
                return None
            return payload
        except Exception:
            return None