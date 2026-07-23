"""
Sistema Financiero - Setup Schemas
Pydantic models for the setup wizard endpoints.
"""
from typing import Literal, Optional

from pydantic import BaseModel, Field

Provider = Literal["telegram", "gemini", "google"]


class ValidateRequest(BaseModel):
    """Body for POST /api/setup/validate — validate one credential live."""
    provider: Provider
    value: str = Field(..., min_length=8, max_length=4096)


class ValidateResponse(BaseModel):
    """Response for a single credential validation."""
    valid: bool
    message: Optional[str] = None
    detail: Optional[str] = None


class StatusResponse(BaseModel):
    """Response for GET /api/setup/status."""
    completed: bool
    tenant_name: Optional[str] = None


class FinalizeRequest(BaseModel):
    """Body for POST /api/setup/finalize — persist everything and restart bot."""
    tenant_name: str = Field(..., min_length=1, max_length=255)
    timezone: str = "America/Mexico_City"
    currency: str = "MXN"

    # Encrypted only in storage; transported over HTTPS as plain string.
    telegram_bot_token: str = Field(..., min_length=20)
    gemini_api_key: str = Field(..., min_length=20)

    # For the Google step we accept both: client_id+secret OR refresh_token (legacy).
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_refresh_token: Optional[str] = None


class FinalizeResponse(BaseModel):
    success: bool
    tenant_id: str
    bot_restart_triggered: bool
    message: str
