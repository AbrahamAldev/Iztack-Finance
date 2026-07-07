"""
Iztack-Finance - Auth Dependencies
FastAPI dependencies for JWT authentication.
"""
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.modules.auth.service import AuthService
from app.database.models import User

# Bearer token prefix
SECURITY = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(SECURITY),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get the current authenticated user from JWT token.
    Raises 401 if not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="No autorizado. Token faltante.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = AuthService.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Token inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await AuthService(db).get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Cuenta desactivada.",
        )

    return user


async def get_current_user_id(
    user: User = Depends(get_current_user),
) -> str:
    """Get just the user ID (convenience dependency)."""
    return user.id