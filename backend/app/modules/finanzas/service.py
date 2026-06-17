"""
Sistema Financiero - Financial Analysis Service
Generates spending analysis, detects money leaks, and provides savings recommendations.
"""
import logging
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class CategorySpending:
    """Spending breakdown by category."""
    category: str
    amount: float
    percentage: float
    trend: str  # up, down, stable
    previous_amount: float


@dataclass
class MoneyLeak:
    """Detected money leak."""
    product: str
    store: str
    current_cost: float
    optimized_cost: float
    monthly_savings: float
    yearly_savings: float
    recommendation: str


@dataclass
class MonthlyReport:
    """Complete monthly financial report."""
    period: str
    total_spent: float
    by_category: List[CategorySpending]
    by_store: Dict[str, float]
    leaks: List[MoneyLeak]
    savings_goal: Dict
    top_products: List[Dict]
    summary: str


class FinancialAnalysisService:
    """Analyzes spending patterns and generates financial insights."""

    def __init__(self):
        self.essential_categories = {
            "alimentos", "bebidas", "higiene", "limpieza",
            "salud", "combustible", "hogar"
        }

    async def generate_monthly_report(self, user_id: str, year: int, month: int) -> MonthlyReport:
        """
        Generate a complete monthly financial report.
        In production, this queries the database. For now, returns structure.
        """
        # TODO: Query from tickets table in database
        return MonthlyReport(
            period=f"{year}-{month:02d}",
            total_spent=0,
            by_category=[],
            by_store={},
            leaks=[],
            savings_goal=self._calculate_savings_goal({}),
            top_products=[],
            summary="Aún no hay datos suficientes. Sigue enviando tickets para obtener análisis."
        )

    def _calculate_savings_goal(self, expenses: Dict[str, float], 
                                  target_percent: float = 15) -> Dict:
        """Calculate weekly savings goal."""
        total = sum(expenses.values())
        if total == 0:
            return {
                "target_savings": 0,
                "weekly_goal": 0,
                "monthly_goal": 0,
                "recommendation": "Comienza a capturar tickets para recibir recomendaciones personalizadas."
            }
        
        monthly_target = total * (target_percent / 100)
        weekly_goal = monthly_target / 4.33
        
        return {
            "target_savings": round(monthly_target, 2),
            "weekly_goal": round(weekly_goal, 2),
            "monthly_goal": round(monthly_target, 2),
            "recommendation": (
                f"Ahorra ${weekly_goal:.0f}/semana para tener ${monthly_target:.0f} al mes "
                f"para compras planeadas sin esfuerzo."
            ),
        }

    def detect_leaks(self, products: List[Dict]) -> List[MoneyLeak]:
        """
        Analyze purchase history to detect money leaks.
        
        Example: Buying small packs vs bulk, frequent small purchases, etc.
        """
        leaks = []
        
        # Group products by name to find recurring purchases
        from collections import Counter
        product_counts = Counter(p["name"] for p in products if p.get("name"))
        
        for product_name, count in product_counts.items():
            if count < 3:  # Need at least 3 purchases to detect pattern
                continue
            
            product_prices = [
                p for p in products 
                if p.get("name") == product_name and p.get("total_price")
            ]
            
            if not product_prices:
                continue
            
            avg_price = sum(p["total_price"] for p in product_prices) / len(product_prices)
            
            # Detect if buying in small quantities (potential leak)
            if count >= 4 and avg_price < 50:
                monthly_cost = avg_price * count
                leaks.append(MoneyLeak(
                    product=product_name,
                    store=product_prices[0].get("store", ""),
                    current_cost=monthly_cost,
                    optimized_cost=monthly_cost * 0.6,  # 40% savings buying bulk
                    monthly_savings=monthly_cost * 0.4,
                    yearly_savings=monthly_cost * 0.4 * 12,
                    recommendation=(
                        f"Estás comprando {product_name} {count} veces/mes "
                        f"a un promedio de ${avg_price:.0f} c/u. "
                        f"Comprando en mayoreo podrías ahorrar hasta "
                        f"${monthly_cost * 0.4:.0f}/mes."
                    )
                ))
        
        return leaks

    def analyze_spending_trend(self, current: float, previous: float) -> str:
        """Analyze if spending is trending up, down, or stable."""
        if previous == 0:
            return "stable"
        change = ((current - previous) / previous) * 100
        if change > 10:
            return "up"
        elif change < -10:
            return "down"
        return "stable"

    def get_spending_summary(self, expenses: Dict[str, float]) -> str:
        """Generate a human-readable spending summary."""
        if not expenses:
            return "No hay datos de gastos todavía."
        
        total = sum(expenses.values())
        essentials = sum(
            v for k, v in expenses.items() 
            if k in self.essential_categories
        )
        discretionary = total - essentials
        essentials_pct = (essentials / total * 100) if total > 0 else 0
        
        top_category = max(expenses, key=expenses.get)
        
        return (
            f"📊 *Resumen Mensual*\n\n"
            f"💰 Total gastado: **${total:,.2f}**\n"
            f"🛒 Gastos esenciales: ${essentials:,.2f} ({essentials_pct:.0f}%)\n"
            f"🎮 Gastos discrecionales: ${discretionary:,.2f}\n"
            f"📈 Mayor gasto: {top_category.title()}: ${expenses[top_category]:,.2f}\n\n"
            f"💡 *Recomendación:* "
            f"{'Tus gastos esenciales son altos. Revisa oportunidades de ahorro en '
              f'alimentos y servicios.' if essentials_pct > 70 else "
              f'Tienes un buen balance. Sigue así!'}"
        )

    def predict_next_month(self, historical: List[Dict]) -> Dict:
        """
        Simple prediction for next month's spending based on historical data.
        Uses average of last 3 months.
        """
        if len(historical) < 2:
            return {"prediction": 0, "confidence": "low"}
        
        recent = historical[-3:] if len(historical) >= 3 else historical
        avg_spending = sum(m.get("total", 0) for m in recent) / len(recent)
        
        # Simple trend-based adjustment
        if len(recent) >= 2:
            last_two = recent[-2:]
            change = last_two[1].get("total", 0) - last_two[0].get("total", 0)
            prediction = avg_spending + (change * 0.5)  # Partial trend continuation
        else:
            prediction = avg_spending
        
        return {
            "prediction": round(prediction, 2),
            "based_on_months": len(recent),
            "confidence": "high" if len(recent) >= 3 else "medium",
        }
</output>
</write_to_file>