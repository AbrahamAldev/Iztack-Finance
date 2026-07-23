"""Iztack-Finance - Business Service. Multi-negocio familiar."""
import logging
from datetime import date, timedelta
from typing import Dict, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Business, Ticket

logger = logging.getLogger(__name__)


class BusinessService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_businesses(self, user_id: str) -> List[Dict]:
        result = await self.db.execute(
            select(Business).where(
                Business.user_id == user_id,
                Business.is_active.is_(True),
            ).order_by(Business.created_at.desc())
        )
        businesses = result.scalars().all()

        # Aggregate ticket counts per user (business_id not yet linked to tickets)
        count_result = await self.db.execute(
            select(func.count(Ticket.id)).where(Ticket.user_id == user_id)
        )
        total_tickets = count_result.scalar() or 0

        return [
            {
                "id": b.id,
                "user_id": b.user_id,
                "name": b.name,
                "description": b.description or "",
                "currency": b.currency,
                "is_active": b.is_active,
                "created_at": b.created_at.isoformat() if b.created_at else None,
                "updated_at": b.updated_at.isoformat() if b.updated_at else None,
                "total_tickets": total_tickets,
            }
            for b in businesses
        ]

    async def create_business(
        self, user_id: str, name: str, description: str = "", currency: str = "MXN"
    ) -> Dict:
        business = Business(
            user_id=user_id,
            name=name.strip(),
            description=description.strip() if description else None,
            currency=currency.upper(),
            is_active=True,
        )
        self.db.add(business)
        await self.db.commit()
        await self.db.refresh(business)
        logger.info(f"Business created: {business.name} for user {user_id}")
        return {
            "id": business.id,
            "user_id": business.user_id,
            "name": business.name,
            "description": business.description or "",
            "currency": business.currency,
            "is_active": business.is_active,
            "total_tickets": 0,
        }

    async def update_business(self, user_id: str, business_id: str, data: Dict) -> Dict:
        result = await self.db.execute(
            select(Business).where(
                Business.id == business_id,
                Business.user_id == user_id,
                Business.is_active.is_(True),
            )
        )
        business = result.scalar_one_or_none()
        if not business:
            raise ValueError("Negocio no encontrado")

        allowed = {"name", "description", "currency"}
        for key, value in data.items():
            if key in allowed:
                if isinstance(value, str):
                    value = value.strip()
                setattr(business, key, value)

        await self.db.commit()
        await self.db.refresh(business)
        return {
            "id": business.id,
            "user_id": business.user_id,
            "name": business.name,
            "description": business.description or "",
            "currency": business.currency,
            "is_active": business.is_active,
        }

    async def deactivate_business(self, user_id: str, business_id: str) -> None:
        result = await self.db.execute(
            select(Business).where(
                Business.id == business_id,
                Business.user_id == user_id,
                Business.is_active.is_(True),
            )
        )
        business = result.scalar_one_or_none()
        if not business:
            raise ValueError("Negocio no encontrado")

        business.is_active = False
        await self.db.commit()
        logger.info(f"Business deactivated: {business_id}")

    async def get_business_summary(self, user_id: str, business_id: str) -> Dict:
        # Verify business exists and belongs to user
        result = await self.db.execute(
            select(Business).where(
                Business.id == business_id,
                Business.user_id == user_id,
            )
        )
        business = result.scalar_one_or_none()
        if not business:
            raise ValueError("Negocio no encontrado")

        thirty_days = date.today() - timedelta(days=30)
        spent_result = await self.db.execute(
            select(func.sum(Ticket.total_amount)).where(
                Ticket.user_id == user_id,
                Ticket.purchase_date >= thirty_days,
            )
        )
        total_30d = spent_result.scalar() or 0
        return {
            "business_id": business_id,
            "business_name": business.name,
            "spent_30d": float(total_30d),
            "currency": business.currency,
        }
