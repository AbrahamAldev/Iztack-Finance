"""
Iztack-Finance - Warranty Routes
API endpoints for warranty tracking and alerts.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import Product, User
from app.modules.auth.deps import get_current_user
from app.modules.garantias.service import WarrantyService
from app.modules.tickets.tracer import trace_step

router = APIRouter(prefix="/api/garantias", tags=["Garantías"])


@router.get("/")
async def list_warranties(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List products with warranty for the current user."""
    query = select(Product).join(Product.ticket).where(
        Product.ticket.has(user_id=current_user.id),
        Product.has_warranty.is_(True),
    )
    if status:
        # Status filtering is done in Python after fetching because warranty
        # status depends on computed end_date.
        pass

    result = await db.execute(query.order_by(Product.warranty_end_date))
    products = result.scalars().all()

    items = []
    __import__("datetime").date.today()
    trace_step(
        user_id=current_user.id,
        step="warranty_list",
        status="ok",
        details={"count": len(products)},
    )
    for product in products:
        if not product.ticket or not product.ticket.purchase_date:
            continue
        warranty = WarrantyService.get_warranty_status(
            purchase_date=product.ticket.purchase_date,
            category=product.category or "otros",
            price=product.total_price or 0,
        )
        if status and warranty.get("status") != status:
            continue
        items.append({
            "product_id": product.id,
            "name": product.name,
            "store": product.ticket.store_name,
            "purchase_date": product.ticket.purchase_date.isoformat(),
            "warranty_end_date": warranty.get("end_date").isoformat() if warranty.get("end_date") else None,
            "days_remaining": warranty.get("days_remaining"),
            "status": warranty.get("status"),
            "alert": warranty.get("alert"),
        })

    return {"warranties": items, "count": len(items)}


@router.get("/alerts")
async def warranty_alerts(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get warranties expiring within the next N days."""
    if days <= 0:
        raise HTTPException(status_code=400, detail="El parámetro 'days' debe ser mayor a 0")

    result = await db.execute(
        select(Product).join(Product.ticket).where(
            Product.ticket.has(user_id=current_user.id),
            Product.has_warranty.is_(True),
            Product.warranty_end_date.isnot(None),
        ).order_by(Product.warranty_end_date)
    )
    products = result.scalars().all()

    today = __import__("datetime").date.today()
    alerts = []
    for product in products:
        if not product.warranty_end_date:
            continue
        days_remaining = (product.warranty_end_date - today).days
        if 0 <= days_remaining <= days:
            alerts.append({
                "product_id": product.id,
                "name": product.name,
                "store": product.ticket.store_name if product.ticket else None,
                "warranty_end_date": product.warranty_end_date.isoformat(),
                "days_remaining": days_remaining,
                "alert": (
                    f"🔧 La garantía de '{product.name}' vence en {days_remaining} días "
                    f"({product.warranty_end_date.strftime('%d/%m/%Y')})."
                ),
            })

    trace_step(
        user_id=current_user.id,
        step="warranty_alerts",
        status="ok",
        details={"count": len(alerts), "days": days},
    )
    return {"alerts": alerts, "count": len(alerts)}
