"""
Iztack-Finance - Dashboard Service
Real-time dashboard data from user's tickets, products, and invoices.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Ticket, Product, Invoice, User

logger = logging.getLogger(__name__)


class DashboardService:
    """Provides real dashboard data for authenticated users."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overview(self, user_id: str) -> dict:
        """Get dashboard overview with KPIs and recent activity."""
        now = datetime.utcnow()
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Monthly spending
        monthly_spent = await self._get_monthly_spent(user_id, first_of_month)

        # Average ticket
        avg_ticket = await self._get_avg_ticket(user_id)

        # Pending invoices
        pending_invoices = await self._get_pending_invoices(user_id)

        # Active warranties
        active_warranties = await self._get_active_warranties(user_id)

        # Recent tickets
        recent_tickets = await self._get_recent_tickets(user_id)

        # Spending by category
        spending_by_category = await self._get_spending_by_category(user_id, first_of_month)

        # Spending by store
        spending_by_store = await self._get_spending_by_store(user_id, first_of_month)

        return {
            "kpi": {
                "monthly_spent": monthly_spent,
                "avg_ticket": avg_ticket,
                "pending_invoices": pending_invoices,
                "active_warranties": active_warranties,
            },
            "recent_tickets": recent_tickets,
            "charts": {
                "by_category": spending_by_category,
                "by_store": spending_by_store,
            },
        }

    async def _get_monthly_spent(self, user_id: str, since: datetime) -> float:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Ticket.total_amount), 0))
            .where(
                Ticket.user_id == user_id,
                Ticket.created_at >= since,
            )
        )
        return float(result.scalar())

    async def _get_avg_ticket(self, user_id: str) -> float:
        result = await self.db.execute(
            select(func.coalesce(func.avg(Ticket.total_amount), 0))
            .where(Ticket.user_id == user_id)
        )
        return round(float(result.scalar()), 2)

    async def _get_pending_invoices(self, user_id: str) -> int:
        from app.database.models import InvoiceStatus
        result = await self.db.execute(
            select(func.count())
            .select_from(Ticket)
            .where(
                Ticket.user_id == user_id,
                Ticket.invoice_status == InvoiceStatus.PENDING.value,
            )
        )
        return result.scalar()

    async def _get_active_warranties(self, user_id: str) -> int:
        now = datetime.utcnow()
        result = await self.db.execute(
            select(func.count())
            .select_from(Product)
            .join(Ticket, Product.ticket_id == Ticket.id)
            .where(
                Ticket.user_id == user_id,
                Product.has_warranty == True,
            )
        )
        return result.scalar()

    async def _get_recent_tickets(self, user_id: str, limit: int = 10) -> list:
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.user_id == user_id)
            .order_by(desc(Ticket.created_at))
            .limit(limit)
        )
        tickets = result.scalars().all()
        return [
            {
                "id": t.id,
                "store_name": t.store_name,
                "total_amount": t.total_amount,
                "purchase_date": t.purchase_date.isoformat() if t.purchase_date else None,
                "status": t.status,
                "has_warranty": t.has_warranty_items,
                "product_count": len(t.products) if t.products else 0,
            }
            for t in tickets
        ]

    async def _get_spending_by_category(self, user_id: str, since: datetime) -> list:
        from sqlalchemy import case
        result = await self.db.execute(
            select(
                Product.category,
                func.coalesce(func.sum(Product.total_price), 0),
            )
            .join(Ticket, Product.ticket_id == Ticket.id)
            .where(
                Ticket.user_id == user_id,
                Ticket.created_at >= since,
                Product.category.isnot(None),
            )
            .group_by(Product.category)
            .order_by(desc(func.sum(Product.total_price)))
        )
        rows = result.all()
        return [{"category": r[0], "amount": float(r[1])} for r in rows]

    async def _get_spending_by_store(self, user_id: str, since: datetime) -> list:
        result = await self.db.execute(
            select(
                Ticket.store_name,
                func.coalesce(func.sum(Ticket.total_amount), 0),
            )
            .where(
                Ticket.user_id == user_id,
                Ticket.created_at >= since,
            )
            .group_by(Ticket.store_name)
            .order_by(desc(func.sum(Ticket.total_amount)))
        )
        rows = result.all()
        return [{"store": r[0], "amount": float(r[1])} for r in rows]