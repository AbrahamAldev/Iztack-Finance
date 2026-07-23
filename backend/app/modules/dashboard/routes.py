"""
Iztack-Finance - Dashboard Routes
API endpoints for real-time dashboard data.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import User
from app.modules.auth.deps import get_current_user
from app.modules.dashboard.service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/overview")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard overview with real KPIs and charts."""
    service = DashboardService(db)
    data = await service.get_overview(current_user.id)
    return data
