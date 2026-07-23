"""
Sistema Financiero - Classification Service
Categorizes products, detects warranties, and classifies expenses.
"""
import logging
from datetime import date
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# Product categories mapping
# =============================================================================

# Keywords for classifying products into categories
PRODUCT_CATEGORY_KEYWORDS = {
    "alimentos": [
        "leche", "pan", "huevo", "arroz", "frijol", "azucar", "cafe", "tortilla",
        "pasta", "galleta", "cereal", "aceite", "sal", "salsa", "atun", "sardina",
        "verduras", "frutas", "carne", "pollo", "pescado", "embutido", "queso",
        "yogur", "mantequilla", "crema", "mermelada", "chocolate", "dulce",
        "botana", "sopa", "consome", "harina", "levadura", "especia",
        "avena", "quinoa", "lenteja", "garbanzo", "chile"
    ],
    "bebidas": [
        "agua", "refresco", "jugo", "cerveza", "vino", "tequila", "whisky",
        "vodka", "ron", "agua mineral", "gatorade", "powerade", "boing",
        "coca", "pepsi", "sprite", "fanta", "sidral", "sangria"
    ],
    "hogar": [
        "jabon", "shampoo", "acondicionador", "crema corporal", "desodorante",
        "papel higienico", "servilleta", "toalla", "cobija", "sabana",
        "cojin", "almohada", "cortina", "tapete", "vela", "ambiental",
        "detergente", "suavizante", "cloro", "limpiador", "trapeador",
        "escoba", "jerga", "esponja", "fabuloso", "pinol"
    ],
    "electronicos": [
        "television", "televisor", "televisores", "tv", "monitor", "laptop", "computadora", "tablet",
        "celular", "telefono", "audifonos", "bocina", "parlante",
        "cargador", "cable", "hub", "router", "modem", "disco duro",
        "memoria usb", "teclado", "mouse", "webcam", "impresora",
        "cafetera", "licuadora", "batidora", "microondas", "estufa",
        "refrigerador", "lavadora", "secadora", "aspiradora", "plancha",
        "ventilador", "clima", "calentador", "freidora", "air fryer"
    ],
    "muebles": [
        "sillon", "sofa", "cama", "colchon", "box", "comoda", "ropero",
        "armario", "mesa", "silla", "escritorio", "estante", "librero",
        "buro", "cabecera", "tocador", "banco", "taburete"
    ],
    "ropa": [
        "camisa", "playera", "pantalon", "short", "vestido", "falda",
        "chamarra", "abrigo", "sueter", "bufanda", "calcetines", "medias",
        "zapatos", "tenis", "sandalias", "ropa interior", "calzon",
        "brasier", "traje", "corbata", "cinturon", "gorra", "sombrero"
    ],
    "salud": [
        "medicina", "pastilla", "jarabe", "vitamina", "suplemento",
        "cura", "gasa", "venda", "termometro", "preservativo",
        "anticonceptivo", "alcohol", "agua oxigenada", "jeringa"
    ],
    "herramientas": [
        "taladro", "martillo", "desarmador", "llave", "pinza", "segueta",
        "sierra", "cinta metrica", "nivel", "lija", "tornillo", "clavo",
        "taquete", "silicon", "pegamento", "candado", "cadena"
    ],
    "automotriz": [
        "aceite motor", "llanta", "neumatico", "bateria", "filtro",
        "bujia", "liquido frenos", "anticonjelante", "refrigerante",
        "pastilla freno", "disco freno", "amortiguador", "escape"
    ],
    "combustible": [
        "gasolina", "diesel", "magna", "premium", "gas", "lp", "natural"
    ],
    "higiene": [
        "jabon manos", "jabon cuerpo", "crema dental", "pasta dental",
        "cepillo dental", "hilo dental", "enjuague bucal", "rasuradora",
        "rastrillo", "crema rasurar", "toalla femenina", "tampon",
        "panal", "toallita humeda", "cottonete", "hisopo",
        "papel higienico", "kleenex", "panuelo"
    ],
    "limpieza": [
        "detergente ropa", "suavizante", "cloro", "limpiador pisos",
        "limpiador vidrios", "fabuloso", "pinol", "ajax", "vanish",
        "quitamanchas", "desengrasante", "jabon trastes", "estropajo",
        "bolsa basura", "film", "papel aluminio", "papel encerado"
    ],
    "entretenimiento": [
        "libro", "revista", "videojuego", "pelicula", "musica",
        "juego mesa", "rompecabezas", "juguete", "pelota"
    ],
}


# High-value items that typically have warranty
HIGH_VALUE_CATEGORIES = {
    "electronicos", "muebles", "herramientas",
}
HIGH_VALUE_PRICE_THRESHOLD = 500.0  # MXN - items above this may have warranty


# Consumable products (no warranty)
CONSUMABLE_CATEGORIES = {
    "alimentos", "bebidas", "higiene", "limpieza", "combustible",
    "salud", "entretenimiento",
}


class ClassificationService:
    """Service for classifying products, stores, and expenses."""

    @staticmethod
    def classify_product(product_name: str, price: float = 0) -> dict:
        """
        Classify a product into a category and determine warranty status.
        
        Returns:
            dict with: category, has_warranty, is_consumable, is_high_value
        """
        name_lower = product_name.lower().strip()

        # Find matching category
        category = "otros"
        for cat, keywords in PRODUCT_CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in name_lower:
                    category = cat
                    break
            if category != "otros":
                break

        # Determine if high value
        is_high_value = price >= HIGH_VALUE_PRICE_THRESHOLD if price else False

        # Determine warranty
        has_warranty = (
            category in HIGH_VALUE_CATEGORIES or
            (is_high_value and category not in CONSUMABLE_CATEGORIES)
        )

        # Determine if consumable
        is_consumable = category in CONSUMABLE_CATEGORIES

        return {
            "category": category,
            "has_warranty": has_warranty,
            "is_consumable": is_consumable,
            "is_high_value": is_high_value,
        }

    @staticmethod
    def check_expired_ticket(purchase_date: date, max_days: int = 60) -> Tuple[bool, int]:
        """
        Check if a ticket is expired for invoicing purposes.
        In Mexico, most stores allow up to 60 days for CFDI requests.
        
        Returns:
            Tuple of (is_expired, days_remaining)
        """
        if not purchase_date:
            return True, 0

        today = date.today()
        days_elapsed = (today - purchase_date).days
        days_remaining = max_days - days_elapsed

        return days_elapsed > max_days, days_remaining

    @staticmethod
    def get_warranty_period(category: str, price: float) -> int:
        """
        Get warranty period in months based on product category and price.
        
        Returns:
            Months of warranty (standard Mexican warranty periods)
        """
        if category in {"electronicos", "herramientas"}:
            if price >= 3000:
                return 36  # 3 years for expensive electronics
            return 12  # 1 year standard

        if category == "muebles":
            if price >= 5000:
                return 60  # 5 years for expensive furniture
            return 24  # 2 years standard

        if category == "automotriz":
            return 36  # 3 years for auto parts

        return 0  # No warranty for other categories

    @staticmethod
    def estimate_consumption_cycle(product_name: str, category: str) -> Optional[int]:
        """
        Estimate consumption cycle in days based on product category.
        Used for the smart shopping list before actual data is available.
        
        Returns:
            Estimated days between purchases, or None if not applicable
        """
        name_lower = product_name.lower()

        # Weekly consumables
        weekly_keywords = ["leche", "pan", "huevo", "tortilla", "yogur", "fruta",
                          "verdura", "carne", "pollo", "pescado", "agua", "refresco"]
        for keyword in weekly_keywords:
            if keyword in name_lower:
                return 7

        # Bi-weekly consumables
        biweekly_keywords = ["arroz", "frijol", "pasta", "aceite", "cereal", "galleta",
                            "queso", "jabon", "shampoo", "papel higienico", "servilleta"]
        for keyword in biweekly_keywords:
            if keyword in name_lower:
                return 15

        # Monthly consumables
        monthly_keywords = ["detergente", "suavizante", "cloro", "limpiador",
                           "fabuloso", "pinol", "desodorante", "crema", "pasta dental"]
        for keyword in monthly_keywords:
            if keyword in name_lower:
                return 30

        # Quarterly
        if category in {"limpieza", "higiene"}:
            return 90

        return None  # Not a consumable / irregular cycle

    @staticmethod
    def detect_money_leak(product_name: str, unit_price: float,
                           bulk_price: float, bulk_quantity: int) -> dict:
        """
        Detect if buying smaller quantities is a money leak vs bulk.
        
        Example:
            Product: "Papel Higiénico"
            Unit price: $25 (4 rollos)
            Bulk price: $85 (12 rollos)
            Result: "Estás gastando $75/12 rollos vs $85 = ahorras $0.83/rollo comprando el paquete grande"
        """
        unit_cost = unit_price
        bulk_unit_cost = bulk_price / bulk_quantity

        savings_per_unit = unit_cost - bulk_unit_cost
        savings_percentage = (savings_per_unit / unit_cost) * 100 if unit_cost > 0 else 0

        return {
            "has_leak": savings_per_unit > 0,
            "product": product_name,
            "current_cost_per_unit": unit_cost,
            "bulk_cost_per_unit": bulk_unit_cost,
            "savings_per_unit": savings_per_unit,
            "savings_percentage": savings_percentage,
            "recommendation": (
                f"Comprar el paquete grande ahorra ${savings_per_unit:.2f} "
                f"por unidad ({savings_percentage:.0f}% de ahorro)"
            ) if savings_per_unit > 0 else "Ya estás comprando la opción más económica"
        }

    @staticmethod
    def calculate_savings_goal(monthly_expenses: dict, target_savings_percent: float = 15) -> dict:
        """
        Calculate savings goals based on current expenses.
        
        Args:
            monthly_expenses: dict with category -> amount
            target_savings_percent: target savings percentage (default 15%)
            
        Returns:
            dict with savings analysis
        """
        total = sum(monthly_expenses.values())
        target_savings = total * (target_savings_percent / 100)
        weekly_savings = target_savings / 4.33  # Average weeks per month

        # Essential vs discretionary
        essential_categories = {"alimentos", "bebidas", "higiene", "limpieza",
                                 "salud", "combustible", "hogar"}
        essential_spending = sum(
            amt for cat, amt in monthly_expenses.items()
            if cat in essential_categories
        )
        discretionary_spending = total - essential_spending

        return {
            "total_monthly_expenses": total,
            "target_savings_percent": target_savings_percent,
            "target_monthly_savings": round(target_savings, 2),
            "weekly_savings_goal": round(weekly_savings, 2),
            "essential_spending": round(essential_spending, 2),
            "discretionary_spending": round(discretionary_spending, 2),
            "potential_savings_from_discretionary": round(
                discretionary_spending * 0.3, 2  # Can save ~30% from discretionary
            ),
            "recommendation": (
                f"Ahorrando ${weekly_savings:.0f} por semana ({target_savings_percent}% de tus ingresos), "
                f"tendrás ${target_savings:.0f} al mes para compras planeadas sin esfuerzo."
            ),
        }
