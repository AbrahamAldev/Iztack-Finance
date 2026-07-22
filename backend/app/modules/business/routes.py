"""
Iztack-Finance - Business Routes (Multi-negocio familiar)
CRUD for family businesses with independent tracking.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.modules.auth.deps import get_current_user
from app.modules.business.service import BusinessService
from app.database.models import User

router = APIRouter(prefix="/api/business", tags=["Business"])


@router.get("")
async def list_businesses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all businesses for the current user."""
    service = BusinessService(db)
    businesses = await service.list_businesses(current_user.id)
    return {"businesses": businesses}


@router.post("")
async def create_business(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new business for the current user."""
    name = data.get("name", "").strip()
    description = data.get("description", "")
    currency = data.get("currency", "MXN")

    if not name:
        raise HTTPException(status_code=400, detail="El nombre del negocio es requerido")

    service = BusinessService(db)
    business = await service.create_business(
        user_id=current_user.id,
        name=name,
        description=description,
        currency=currency,
    )
    return {"success": True, "business": business}


@router.put("/{business_id}")
async def update_business(
    business_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a business."""
    service = BusinessService(db)
    business = await service.update_business(
        user_id=current_user.id,
        business_id=business_id,
        data=data,
    )
    return {"success": True, "business": business}


@router.delete("/{business_id}")
async def delete_business(
    business_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete/deactivate a business."""
    service = BusinessService(db)
    await service.deactivate_business(current_user.id, business_id)
    return {"success": True, "message": "Negocio desactivado"}


@router.get("/{business_id}/summary")
async def business_summary(
    business_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get financial summary for a specific business."""
    service = BusinessService(db)
    summary = await service.get_business_summary(current_user.id, business_id)
    return summary