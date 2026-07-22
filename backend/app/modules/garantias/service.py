"""
Sistema Financiero - Warranty Management Service
Tracks products with warranties, alerts when they're about to expire.
"""
import logging
from datetime import date
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class WarrantyService:
    """
    Manages product warranties.
    Detects warrantable products, tracks expiry dates, sends alerts.
    """

    # Categories that typically have warranty
    WARRANTY_CATEGORIES = {
        "electronicos": {"months": 12, "min_price": 500},
        "muebles": {"months": 24, "min_price": 1000},
        "herramientas": {"months": 12, "min_price": 500},
        "automotriz": {"months": 36, "min_price": 500},
    }

    # Extended warranty for high-value items
    EXTENDED_WARRANTY = {
        "electronicos": {"threshold": 5000, "months": 36},
        "muebles": {"threshold": 10000, "months": 60},
        "herramientas": {"threshold": 3000, "months": 24},
    }

    @classmethod
    def is_warrantable(cls, category: str, price: float) -> bool:
        """Check if a product qualifies for warranty tracking."""
        if category in cls.WARRANTY_CATEGORIES:
            rules = cls.WARRANTY_CATEGORIES[category]
            return price >= rules["min_price"]
        return False

    @classmethod
    def get_warranty_months(cls, category: str, price: float) -> int:
        """Get warranty period in months."""
        # Check extended warranty first
        if category in cls.EXTENDED_WARRANTY:
            ext = cls.EXTENDED_WARRANTY[category]
            if price >= ext["threshold"]:
                return ext["months"]
        
        # Standard warranty
        if category in cls.WARRANTY_CATEGORIES:
            return cls.WARRANTY_CATEGORIES[category]["months"]
        
        return 0

    @classmethod
    def get_warranty_end_date(cls, purchase_date: date, category: str, 
                               price: float) -> Optional[date]:
        """Calculate warranty end date."""
        months = cls.get_warranty_months(category, price)
        if months <= 0:
            return None
        
        # Add months to date
        end_month = purchase_date.month + months
        end_year = purchase_date.year + (end_month - 1) // 12
        end_month = ((end_month - 1) % 12) + 1
        
        try:
            return purchase_date.replace(year=end_year, month=end_month)
        except ValueError:
            # Handle end of month edge case
            import calendar
            last_day = calendar.monthrange(end_year, end_month)[1]
            return purchase_date.replace(year=end_year, month=end_month, day=last_day)

    @classmethod
    def get_warranty_status(cls, purchase_date: date, category: str, 
                             price: float) -> Dict:
        """
        Get warranty status with alerts.
        
        Returns:
            dict with: has_warranty, end_date, days_remaining, status, alert
        """
        if not cls.is_warrantable(category, price):
            return {
                "has_warranty": False,
                "end_date": None,
                "days_remaining": 0,
                "status": "no_warranty",
                "alert": None,
            }
        
        end_date = cls.get_warranty_end_date(purchase_date, category, price)
        if not end_date:
            return {"has_warranty": False}
        
        today = date.today()
        days_remaining = (end_date - today).days
        
        # Determine status and alert
        if days_remaining < 0:
            status = "expired"
            alert = None
        elif days_remaining <= 30:
            status = "expiring_soon"
            alert = (
                f"⚠️ La garantía de tu producto ({category}) "
                f"vence en {days_remaining} días ({end_date.strftime('%d/%m/%Y')}). "
                f"Revisa si tienes algún problema antes de que expire."
            )
        elif days_remaining <= 90:
            status = "active"
            alert = (
                f"ℹ️ Tu garantía vence en {days_remaining} días "
                f"({end_date.strftime('%d/%m/%Y')})"
            )
        else:
            status = "active"
            alert = None
        
        return {
            "has_warranty": True,
            "end_date": end_date,
            "days_remaining": days_remaining,
            "status": status,
            "alert": alert,
        }

    @classmethod
    def get_products_to_alert(cls, products: List[Dict]) -> List[Dict]:
        """Get products whose warranty is about to expire."""
        alerts = []
        today = date.today()
        
        for product in products:
            purchase_date = product.get("purchase_date")
            category = product.get("category", "")
            price = product.get("price", 0)
            
            if not purchase_date or not cls.is_warrantable(category, price):
                continue
            
            end_date = cls.get_warranty_end_date(purchase_date, category, price)
            if not end_date:
                continue
            
            days_remaining = (end_date - today).days
            
            # Alert if expiring within 30 days
            if 0 <= days_remaining <= 30:
                alerts.append({
                    "product_name": product.get("name", "Producto"),
                    "category": category,
                    "purchase_date": purchase_date,
                    "end_date": end_date,
                    "days_remaining": days_remaining,
                    "alert": (
                        f"🔧 ¡La garantía de '{product.get('name', 'Producto')}' "
                        f"vence en {days_remaining} días! "
                        f"Fecha de compra: {purchase_date.strftime('%d/%m/%Y')}"
                    ),
                })
        
        return alerts