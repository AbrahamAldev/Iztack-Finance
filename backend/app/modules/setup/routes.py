"""
Sistema Financiero - Setup Routes
HTTP endpoints for the onboarding wizard.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.modules.setup import service
from app.modules.setup.schemas import (
    FinalizeRequest,
    FinalizeResponse,
    StatusResponse,
    ValidateRequest,
    ValidateResponse,
)

router = APIRouter()


@router.get("/status", response_model=StatusResponse, tags=["Setup"])
async def get_status(db: AsyncSession = Depends(get_db)):
    """Returns whether the wizard has been completed already."""
    completed = await service.is_setup_completed(db)
    tenant = await service.get_default_tenant(db) if completed else None
    return StatusResponse(
        completed=completed,
        tenant_name=tenant.name if tenant else None,
    )


@router.post("/validate", response_model=ValidateResponse, tags=["Setup"])
async def validate_credential(req: ValidateRequest):
    """
    Validate ONE credential live (does NOT persist anything).
    Used by the wizard to confirm the token/key works before showing the next step.
    """
    valid, ok_msg, err_msg = await service.validate_credential(req)
    if valid:
        return ValidateResponse(valid=True, message=ok_msg)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=err_msg or "La credencial no es válida.",
    )


@router.post("/finalize", response_model=FinalizeResponse, tags=["Setup"])
async def finalize(req: FinalizeRequest, db: AsyncSession = Depends(get_db)):
    """
    Persist all credentials, mark the tenant as setup_completed, write .env,
    and trigger a restart of the telegram-bot container.
    """
    try:
        tenant = await service.finalize_setup(db, req)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar la configuración: {exc}",
        ) from exc

    return FinalizeResponse(
        success=True,
        tenant_id=tenant.id,
        bot_restart_triggered=True,  # best effort
        message=(
            f"Configuración guardada para el tenant «{tenant.name}». "
            "El bot se está reiniciando con el nuevo token."
        ),
    )