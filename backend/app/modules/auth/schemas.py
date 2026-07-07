"""
Iztack-Finance - Auth Schemas
Pydantic models for authentication requests and responses.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    email: str = Field(..., description="Email del usuario")
    name: str = Field(..., min_length=1, max_length=255, description="Nombre completo")
    password: str = Field(..., min_length=6, max_length=128, description="Contraseña")
    tenant_name: Optional[str] = Field(None, description="Nombre del tenant (familia/organización)")


class LoginRequest(BaseModel):
    email: str = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    tenant_id: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    is_active: bool
    timezone: str
    currency: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    timezone: Optional[str] = None
    currency: Optional[str] = None
    telegram_chat_id: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=128)