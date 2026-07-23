"""
Sistema Financiero - Validation Utilities
Validators for RFC, CURP, emails, amounts, etc.
"""
import re
from datetime import date, datetime


class Validators:
    """Collection of validation methods."""

    @staticmethod
    def validate_rfc(rfc: str) -> bool:
        """
        Validate Mexican RFC (Registro Federal de Contribuyentes).
        Formats:
        - Moral: XXX000000XXX (12 chars)
        - Física: XXXX000000XXX (13 chars)
        """
        if not rfc:
            return False
        rfc = rfc.upper().strip()
        # Persona moral: 12 chars, persona física: 13 chars
        pattern = r'^[A-ZÑ&]{3,4}[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])[A-Z0-9]{2,3}$'
        return bool(re.match(pattern, rfc))

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate Mexican phone number (10 digits)."""
        if not phone:
            return False
        cleaned = re.sub(r'[\s\+\-\(\)]', '', phone)
        return bool(re.match(r'^(\+?52)?\d{10}$', cleaned))

    @staticmethod
    def validate_amount(amount: float) -> bool:
        """Validate a monetary amount is positive and reasonable."""
        if amount is None:
            return False
        return amount >= 0 and amount < 10_000_000  # Max $10M MXN

    @staticmethod
    def validate_date(date_str: str, fmt: str = "%Y-%m-%d") -> bool:
        """Validate a date string format."""
        try:
            datetime.strptime(date_str, fmt)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_invoice_period(purchase_date: date, max_days: int = 60) -> bool:
        """
        Validate that the purchase date is within the allowed period for invoicing.
        In Mexico, CFDI invoices can be requested up to 60 days after purchase (varies by store).
        Returns True if still valid, False if expired.
        """
        if not purchase_date:
            return False
        today = date.today()
        delta = (today - purchase_date).days
        return delta <= max_days

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage."""
        # Remove path separators and special chars
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        if len(filename) > 200:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:195] + '.' + ext
        return filename.strip()

    @staticmethod
    def classify_store_from_name(name: str) -> str:
        """Detect store category from store name."""
        if not name:
            return "other"

        name_lower = name.lower().strip()

        store_map = {
            "liverpool": "liverpool",
            "ikea": "ikea",
            "walmart": "walmart",
            "walmex": "walmart",
            "amazon": "amazon",
            "home depot": "home_depot",
            "the home depot": "home_depot",
            "oxxo": "oxxo",
            "farmacias similares": "farmacias_similares",
            "similares": "farmacias_similares",
            "pemex": "pemex",
            "bp": "bp",
            "costco": "costco",
            "sam's club": "sams_club",
            "sams club": "sams_club",
            "soriana": "soriana",
            "chedraui": "chedraui",
            "comercial mexicana": "walmart",
            "bodega aurrera": "walmart",
            "superama": "walmart",
        }

        for key, value in store_map.items():
            if key in name_lower:
                return value

        return "other"
