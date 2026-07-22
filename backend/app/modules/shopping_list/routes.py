"""
Iztack-Finance - Shopping List Routes
API endpoints for smart shopping lists.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.connection import get_db
from app.modules.auth.deps import get_current_user
from app.database.models import User
from app.modules.shopping_list.service import ShoppingListService
from app.modules.tickets.tracer import trace_step

router = APIRouter(prefix="/api/shopping-list", tags=["Lista de Compras"])


@router.get("/")
async def get_shopping_list(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current active shopping list or generate a new one if none exists."""
    service = ShoppingListService(db)
    current = await service.get_current_list(current_user.id)
    if current:
        trace_step(
            user_id=current_user.id,
            step="shopping_list_get",
            status="ok",
            details={"list_id": current.id, "items_count": len(current.items)},
        )
        return {
            "id": current.id,
            "title": current.title,
            "items": [
                {
                    "name": item.name,
                    "category": item.category,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "estimated_price": item.estimated_price,
                    "preferred_store": item.preferred_store,
                    "priority": item.priority,
                    "auto_generated": item.auto_generated,
                }
                for item in current.items
            ],
            "estimated_total": current.estimated_total,
            "store_grouping": {
                store: [{"name": i.name, "quantity": i.quantity, "unit": i.unit}
                        for i in items]
                for store, items in current.store_grouping.items()
            },
            "created_at": current.created_at,
            "source": current.source,
        }

    # Generate a new list if none active
    generated = await service.generate_weekly_list(current_user.id)
    trace_step(
        user_id=current_user.id,
        step="shopping_list_generate",
        status="ok",
        details={"list_id": generated.id, "items_count": len(generated.items)},
    )
    return {
        "id": generated.id,
        "title": generated.title,
        "items": [
            {
                "name": item.name,
                "category": item.category,
                "quantity": item.quantity,
                "unit": item.unit,
                "estimated_price": item.estimated_price,
                "preferred_store": item.preferred_store,
                "priority": item.priority,
                "auto_generated": item.auto_generated,
            }
            for item in generated.items
        ],
        "estimated_total": generated.estimated_total,
        "store_grouping": {
            store: [{"name": i.name, "quantity": i.quantity, "unit": i.unit}
                    for i in items]
            for store, items in generated.store_grouping.items()
        },
        "created_at": generated.created_at,
        "source": generated.source,
    }


@router.post("/generate")
async def generate_shopping_list(
    title: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new weekly shopping list for the current user."""
    service = ShoppingListService(db)
    generated = await service.generate_weekly_list(current_user.id, title=title)
    trace_step(
        user_id=current_user.id,
        step="shopping_list_generate",
        status="ok",
        details={"list_id": generated.id, "items_count": len(generated.items), "title": title},
    )
    return {
        "id": generated.id,
        "title": generated.title,
        "items": [
            {
                "name": item.name,
                "category": item.category,
                "quantity": item.quantity,
                "unit": item.unit,
                "estimated_price": item.estimated_price,
                "preferred_store": item.preferred_store,
                "priority": item.priority,
                "auto_generated": item.auto_generated,
            }
            for item in generated.items
        ],
        "estimated_total": generated.estimated_total,
        "created_at": generated.created_at,
        "source": generated.source,
    }


@router.post("/{list_id}/print")
async def format_for_print(
    list_id: str,
    width: int = 57,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return a thermal-printer-friendly format of the shopping list."""
    service = ShoppingListService(db)
    current = await service.get_current_list(current_user.id)
    if not current or current.id != list_id:
        raise HTTPException(status_code=404, detail="Lista no encontrada")
    return {"formatted": service.format_for_printer(current, width=width)}
