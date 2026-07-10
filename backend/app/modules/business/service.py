"""Iztack-Finance - Business Service. Multi-negocio familiar."""
import logging
from datetime import date, timedelta
from typing import List, Dict, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Ticket, Product, User

logger = logging.getLogger(__name__)

# In-memory storage for businesses (TODO: create Business model in DB)
_businesses = {}


class BusinessService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_businesses(self, user_id: str) -> List[Dict]:
        businesses = _businesses.get(user_id, [])
        # Add ticket count per business
        for b in businesses:
            result = await self.db.execute(
                select(func.count(Ticket.id)).where(Ticket.user_id == user_id)
            )
            b["total_tickets"] = result.scalar() or 0
        return businesses

    async def create_business(self, user_id: str, name: str, description: str = "", currency: str = "MXN") -> Dict:
        import uuid
        business = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": name,
            "description": description,
            "currency": currency,
            "is_active": True,
            "total_tickets": 0,
        }
        if user_id not in _businesses:
            _businesses[user_id] = []
        _businesses[user_id].append(business)
        return business

    async def update_business(self, user_id: str, business_id: str, data: Dict) -> Dict:
        businesses = _businesses.get(user_id, [])
        for i, b in enumerate(businesses):
            if b["id"] == business_id:
                businesses[i].update({k: v for k, v in data.items() if k in ("name", "description", "currency")})
                return businesses[i]
        raise ValueError("Negocio no encontrado")

    async def deactivate_business(self, user_id: str, business_id: str):
        businesses = _businesses.get(user_id, [])
        for b in businesses:
            if b["id"] == business_id:
                b["is_active"] = False
                return
        raise ValueError("Negocio no encontrado")

    async def get_business_summary(self, user_id: str, business_id: str) -> Dict:
        # Return summary of last 30 days
        thirty_days = date.today() - timedelta(days=30)
        result = await self.db.execute(
            select(func.sum(Ticket.total_amount)).where(
                Ticket.user_id == user_id,
                Ticket.purchase_date >= thirty_days,
            )
        )
        total_30d = result.scalar() or 0
        return {
            "business_id": business_id,
            "spent_30d": float(total_30d),
        }