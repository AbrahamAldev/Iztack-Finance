"""
Iztack-Finance - Financial Analysis Service v2
Generates spending analysis, detects money leaks from real DB data.
"""
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Product, Ticket

logger = logging.getLogger(__name__)


@dataclass
class CategorySpending:
    category: str
    amount: float
    percentage: float
    trend: str
    previous_amount: float


@dataclass
class MoneyLeak:
    product: str
    store: str
    frequency_per_month: int
    avg_price: float
    optimized_cost: float
    monthly_savings: float
    yearly_savings: float
    recommendation: str


@dataclass
class MonthlyReport:
    period: str
    total_spent: float
    by_category: List[CategorySpending]
    by_store: Dict[str, float]
    leaks: List[MoneyLeak]
    savings_goal: Dict
    top_products: List[Dict]
    summary: str


class FinancialAnalysisService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_monthly_report(self, user_id: str, year: int, month: int) -> MonthlyReport:
        start_date = date(year, month, 1)
        end_date = date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)
        prev_start = (start_date.replace(day=1) - timedelta(days=1)).replace(day=1)

        tickets = await self._get_tickets_in_range(user_id, start_date, end_date)
        prev_tickets = await self._get_tickets_in_range(user_id, prev_start, start_date)

        total_spent = sum(t.total_amount for t in tickets if t.total_amount)
        prev_total = sum(t.total_amount for t in prev_tickets if t.total_amount)

        by_category = await self._calculate_category_spending(user_id, start_date, end_date, prev_start)
        by_store = self._calculate_store_spending(tickets)
        leaks = await self._detect_leaks(user_id, start_date, end_date)
        top_products = await self._get_top_products(user_id, start_date, end_date)
        savings_goal = self._calculate_savings_goal(total_spent)
        summary = self._generate_summary(total_spent, prev_total, by_category, leaks)

        return MonthlyReport(
            period=f"{year}-{month:02d}", total_spent=total_spent,
            by_category=by_category, by_store=by_store,
            leaks=leaks, savings_goal=savings_goal,
            top_products=top_products, summary=summary,
        )

    async def _get_tickets_in_range(self, user_id: str, start: date, end: date) -> list:
        result = await self.db.execute(
            select(Ticket).where(Ticket.user_id == user_id, Ticket.purchase_date >= start, Ticket.purchase_date < end)
        )
        return result.scalars().all()

    async def _calculate_category_spending(self, user_id, start, end, prev_start) -> List[CategorySpending]:
        result = await self.db.execute(
            select(Product).join(Ticket).where(
                Ticket.user_id == user_id, Ticket.purchase_date >= start, Ticket.purchase_date < end, Product.category.isnot(None)
            )
        )
        products = result.scalars().all()
        prev_result = await self.db.execute(
            select(Product).join(Ticket).where(
                Ticket.user_id == user_id, Ticket.purchase_date >= prev_start, Ticket.purchase_date < start, Product.category.isnot(None)
            )
        )
        prev_products = prev_result.scalars().all()

        current, previous = defaultdict(float), defaultdict(float)
        for p in products: current[p.category or "otros"] += p.total_price or 0
        for p in prev_products: previous[p.category or "otros"] += p.total_price or 0

        total = sum(current.values()) or 1
        result_list = []
        for cat, amount in sorted(current.items(), key=lambda x: x[1], reverse=True):
            prev_amount = previous.get(cat, 0)
            trend = "up" if prev_amount and amount > prev_amount * 1.05 else "down" if prev_amount and amount < prev_amount * 0.95 else "stable"
            result_list.append(CategorySpending(category=cat, amount=amount, percentage=round(amount / total * 100, 1), trend=trend, previous_amount=prev_amount))
        return result_list

    def _calculate_store_spending(self, tickets: list) -> Dict[str, float]:
        by_store = defaultdict(float)
        for t in tickets: by_store[t.store_name or "Desconocido"] += t.total_amount or 0
        return dict(sorted(by_store.items(), key=lambda x: x[1], reverse=True))

    async def _detect_leaks(self, user_id, start, end) -> List[MoneyLeak]:
        result = await self.db.execute(
            select(Product).join(Ticket).where(
                Ticket.user_id == user_id, Ticket.purchase_date >= start, Ticket.purchase_date < end,
                Product.category.in_(["alimentos", "bebidas", "higiene", "limpieza"]),
                Product.total_price < 200,
            )
        )
        products = result.scalars().all()
        counter, prices = Counter(), defaultdict(list)
        for p in products:
            name = p.name.lower().strip()
            counter[name] += 1
            prices[name].append(p.total_price or 0)

        leaks = []
        for name, freq in counter.most_common(10):
            if freq < 3: continue
            avg_price = sum(prices[name]) / len(prices[name])
            optimized = avg_price * 0.65
            monthly = avg_price * freq
            savings = monthly * 0.35
            leaks.append(MoneyLeak(
                product=name.title(), store="varias", frequency_per_month=freq,
                avg_price=round(avg_price, 2), optimized_cost=round(optimized, 2),
                monthly_savings=round(savings, 2), yearly_savings=round(savings * 12, 2),
                recommendation=f"Comprar {name} en presentación grande ahorra ~${savings:.0f}/mes",
            ))
        return leaks[:5]

    async def _get_top_products(self, user_id, start, end) -> List[Dict]:
        result = await self.db.execute(
            select(Product).join(Ticket).where(Ticket.user_id == user_id, Ticket.purchase_date >= start, Ticket.purchase_date < end)
            .order_by(desc(Product.total_price)).limit(10)
        )
        return [{"name": p.name, "store": p.ticket.store_name if p.ticket else "N/A", "price": p.total_price, "category": p.category} for p in result.scalars().all()]

    def _calculate_savings_goal(self, monthly_spent: float, target_percent: float = 15) -> Dict:
        if monthly_spent == 0:
            return {"weekly_target": 0, "monthly_target": 0, "message": "Sin datos aún"}
        target = monthly_spent * (1 + target_percent / 100)
        weekly = target / 4
        return {"weekly_target": round(weekly, 2), "monthly_target": round(target, 2), "current_spent": round(monthly_spent, 2), "message": f"Ahorra ${weekly:.0f}/semana para tener ${target:.0f} al mes"}

    def _generate_summary(self, total, prev_total, categories, leaks) -> str:
        if total == 0: return "Aún no hay datos. Envía tickets para obtener análisis."
        parts = [f"Total del mes: ${total:,.2f}"]
        if prev_total > 0:
            change = ((total - prev_total) / prev_total) * 100
            parts.append(f"vs mes anterior: {'subió' if change > 0 else 'bajó'} {abs(change):.1f}%")
        if categories: parts.append(f"Principal: {categories[0].category} ({categories[0].percentage}%)")
        if leaks:
            total_sav = sum(l.monthly_savings for l in leaks)
            parts.append(f"🔍 {len(leaks)} fugas — ahorro potencial: ${total_sav:.0f}/mes")
        return " | ".join(parts)
