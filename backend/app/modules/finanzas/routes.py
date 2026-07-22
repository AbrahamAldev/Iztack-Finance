"""
Iztack-Finance - Financial Analysis Routes
API endpoints for spending reports, money leaks, and savings goals.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from app.database.connection import get_db
from app.modules.auth.deps import get_current_user
from app.database.models import User
from app.modules.finanzas.service import FinancialAnalysisService

router = APIRouter(prefix="/api/finanzas", tags=["Finanzas"])


@router.get("/report")
async def get_monthly_report(
    year: Optional[int] = Query(None, description="Año del reporte"),
    month: Optional[int] = Query(None, description="Mes del reporte (1-12)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a monthly financial report for the current user."""
    today = date.today()
    year = year or today.year
    month = month or today.month

    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Mes inválido. Usa 1-12.")

    service = FinancialAnalysisService(db)
    report = await service.generate_monthly_report(
        user_id=current_user.id,
        year=year,
        month=month,
    )

    return {
        "period": report.period,
        "total_spent": report.total_spent,
        "by_category": [
            {
                "category": c.category,
                "amount": c.amount,
                "percentage": c.percentage,
                "trend": c.trend,
                "previous_amount": c.previous_amount,
            }
            for c in report.by_category
        ],
        "by_store": report.by_store,
        "leaks": [
            {
                "product": leak.product,
                "store": leak.store,
                "frequency_per_month": leak.frequency_per_month,
                "avg_price": leak.avg_price,
                "optimized_cost": leak.optimized_cost,
                "monthly_savings": leak.monthly_savings,
                "yearly_savings": leak.yearly_savings,
                "recommendation": leak.recommendation,
            }
            for leak in report.leaks
        ],
        "savings_goal": report.savings_goal,
        "top_products": report.top_products,
        "summary": report.summary,
    }


@router.get("/summary")
async def get_financial_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a quick financial summary for the current month."""
    today = date.today()
    service = FinancialAnalysisService(db)
    report = await service.generate_monthly_report(
        user_id=current_user.id,
        year=today.year,
        month=today.month,
    )
    return {
        "period": report.period,
        "total_spent": report.total_spent,
        "top_category": report.by_category[0].category if report.by_category else None,
        "potential_monthly_savings": sum(leak.monthly_savings for leak in report.leaks),
        "summary": report.summary,
    }
