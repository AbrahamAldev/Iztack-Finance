import io
import logging
import re
from datetime import date, datetime
from typing import Optional

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

from .schemas import OCRResponse, OCRTicketData, OCRProduct

logger = logging.getLogger(__name__)

STORE_KEYWORDS = {
    "liverpool": ["liverpool", "puerta de hierro", "centro londres"],
    "walmart": ["walmart", "walmex", "bodega aurrera", "aurrera"],
    "chedraui": ["chedraui", "súper che", "súper che d"],
    "oxxo": ["oxxo", "extra", "tienda extra"],
    "soriana": ["soriana", "soriana híper", "soriana mercado", "soriana súper"],
    "costco": ["costco", "precio club", "price club"],
    "sams_club": ["sam's club", "sams club"],
    "amazon": ["amazon", "amazon mx", "amazon.com.mx"],
    "home_depot": ["home depot", "the home depot"],
    "ikea": ["ikea"],
    "pemex": ["pemex", "gasolinera"],
    "bp": ["bp", "bp gas"],
    "farmacias_similares": ["similares", "farm. similares"],
    "oxxo_gas": ["oxxo gas"],
}

CATEGORY_KEYWORDS = {
    "alimentos": ["arroz", "frijol", "tortilla", "pan", "leche", "huevo", "carne", "pollo", "pescado", "verdura", "fruta", "comida", "alimento", "despensa", "cereal", "pasta", "sopa", "aceite", "azúcar", "sal", "salsa", "enlatado", "galleta", "chocolate", "dulce", "botana"],
    "bebidas": ["agua", "refresco", "soda", "jugo", "cerveza", "vino", "licor", "café", "té", "bebida", "energética", "isotónica", "leche", "yogur", "yogurt"],
    "hogar": ["limpia", "jabón", "cloro", "suavizante", "detergente", "esponja", "servilleta", "papel", "bolsa", "plato", "vaso", "cubierto", "toalla", "sábana", "cojín", "cortina", "vela", "foco"],
    "higiene": ["shampoo", "jabón", "pasta", "cepillo", "desodorante", "crema", "perfume", "colonia", "rasuradora", "toalla sanitaria", "pañal", "toallita", "papel higiénico", "cuidado personal"],
    "salud": ["medicina", "medicamento", "pastilla", "jarabe", "vitamina", "suplemento", "analgésico", "antiinflamatorio", "curita", "venda", "mascarilla", "gel antibacterial", "farmacia"],
    "electronicos": ["cable", "cargador", "audífono", "bocina", "pantalla", "monitor", "teclado", "mouse", "computadora", "laptop", "tablet", "celular", "teléfono", "reloj", "smartwatch", "batería", "usb", "memoria", "disco duro", "impresora"],
    "muebles": ["silla", "mesa", "escritorio", "cama", "colchón", "sofá", "sillón", "estante", "repisa", "armario", "ropero", "cómoda", "librero"],
    "ropa": ["camisa", "playera", "pantalón", "short", "vestido", "falda", "blusa", "suéter", "chaqueta", "abrigo", "chamarra", "zapato", "tenis", "sandalia", "calcetín", "cinturón", "corbata", "ropa interior"],
    "herramientas": ["martillo", "desarmador", "llave", "pinza", "taladro", "sierra", "cinta", "pegamento", "tornillo", "clavo", "taquete", "lija", "brocha", "pintura"],
    "automotriz": ["aceite", "refrigerante", "líquido", "freno", "batería", "llanta", "neumático", "limpiador", "parabrisas", "aditivo"],
    "combustible": ["gasolina", "magna", "premium", "diesel", "gas", "etanol", "combustible"],
    "entretenimiento": ["juguete", "juego", "película", "libro", "revista", "música", "videojuego", "consola", "suscripción"],
    "servicios": ["recibo", "luz", "agua", "teléfono", "internet", "suscripción", "mensualidad", "renta", "seguro"],
}

CATEGORY_MAP = {
    "alimentos": "alimentos", "bebidas": "bebidas", "hogar": "hogar",
    "higiene": "higiene", "salud": "salud",
    "electronicos": "electronicos", "muebles": "muebles",
    "ropa": "ropa", "herramientas": "herramientas",
    "automotriz": "automotriz", "combustible": "combustible",
    "entretenimiento": "entretenimiento", "servicios": "servicios",
}

WARRANTY_KEYWORDS = ["garantía", "garantia", "warranty", "años de garantía", "meses de garantía"]


class LocalOCRService:

    def preprocess(self, image_bytes: bytes) -> bytes:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != "RGB":
                img = img.convert("RGB")
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.8)
            img = img.filter(ImageFilter.SHARPEN)
            max_dim = 2048
            if max(img.size) > max_dim:
                ratio = max_dim / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=90)
            return buf.getvalue()
        except Exception as e:
            logger.error(f"Preprocess error: {e}")
            return image_bytes

    def extract_text(self, image_bytes: bytes, lang: str = "spa+eng") -> str:
        try:
            processed = self.preprocess(image_bytes)
            img = Image.open(io.BytesIO(processed))
            custom_config = "--oem 3 --psm 4 -c tessedit_char_whitelist='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;/-$%@&()!?+ '"
            text = pytesseract.image_to_string(img, lang=lang, config=custom_config)
            return text.strip()
        except Exception as e:
            logger.error(f"Tesseract error: {e}", exc_info=True)
            return ""


class ReceiptParser:

    def parse(self, raw_text: str) -> OCRResponse:
        if not raw_text.strip():
            return OCRResponse(success=False, error="No se pudo extraer texto del ticket", raw_text="")

        store_name, store_category = self._detect_store(raw_text)
        receipt_number = self._extract_receipt_number(raw_text)
        purchase_date = self._extract_date(raw_text)
        purchase_time = self._extract_time(raw_text)
        subtotal = self._extract_amount(raw_text, ["subtotal", "sub total", "sub-total"])
        taxes = self._extract_amount(raw_text, ["iva", "impuesto", "imp", "tax"])
        total = self._extract_amount(raw_text, ["total"])
        payment_method = self._detect_payment(raw_text)
        products = self._extract_products(raw_text)
        has_warranty = self._check_warranty(products)

        confidence = self._estimate_confidence(raw_text, products)

        data = OCRTicketData(
            store_name=store_name or "Desconocida",
            store_category=store_category,
            receipt_number=receipt_number,
            purchase_date=purchase_date,
            purchase_time=purchase_time,
            subtotal=subtotal,
            taxes=taxes,
            total_amount=total,
            payment_method=payment_method,
            currency="MXN",
            products=products,
            has_warranty_items=has_warranty,
            confidence=confidence,
        )

        return OCRResponse(success=True, data=data, raw_text=raw_text)

    def _detect_store(self, text: str) -> tuple:
        text_lower = text.lower()
        for category, keywords in STORE_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    display_name = category.replace("_", " ").title()
                    return display_name, category
        return "", ""

    def _extract_receipt_number(self, text: str) -> Optional[str]:
        patterns = [
            r"(?:folio|ticket|no\.?|número|#)\s*:?\s*([A-Za-z0-9\-]+)",
            r"(?:factura|venta)\s*:?\s*([A-Za-z0-9\-]+)",
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1)
        return None

    def _extract_date(self, text: str) -> Optional[str]:
        patterns = [
            r"(\d{2})[\/\-](\d{2})[\/\-](\d{4})",
            r"(\d{4})[\/\-](\d{2})[\/\-](\d{2})",
            r"(\d{2})\s*(?:de|del)?\s*([a-z]+)\s*(?:de|del)?\s*(\d{4})",
        ]
        months = {
            "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
            "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5,
            "junio": 6, "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10,
            "noviembre": 11, "diciembre": 12,
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        }

        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                groups = m.groups()
                if len(groups) == 3:
                    if m.lastindex == 3:
                        try:
                            day, month_str, year = groups
                            month = int(month_str) if month_str.isdigit() else months.get(month_str.lower()[:3], 0)
                            if month and 1 <= int(day) <= 31:
                                return f"{year}-{month:02d}-{int(day):02d}"
                        except (ValueError, KeyError):
                            pass
        return None

    def _extract_time(self, text: str) -> Optional[str]:
        m = re.search(r"(\d{1,2}):(\d{2})(?:\s*(?:hrs|am|pm))?", text, re.IGNORECASE)
        if m:
            return f"{int(m.group(1)):02d}:{m.group(2)}"
        return None

    def _extract_amount(self, text: str, labels: list) -> Optional[float]:
        for label in labels:
            patterns = [
                rf"{label}\s*:?\s*\$?\s*(\d+(?:[,.]\d+)?)",
                rf"{label}\s*:?\s*\$?\s*(\d+[.,]\d{2})",
            ]
            for p in patterns:
                m = re.search(p, text, re.IGNORECASE)
                if m:
                    try:
                        val = m.group(1).replace(",", "")
                        return float(val)
                    except ValueError:
                        pass
        return None

    def _detect_payment(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        if any(w in text_lower for w in ["efectivo", "cash", "contado"]):
            return "cash"
        if any(w in text_lower for w in ["credito", "crédito", "credit"]):
            return "credit_card"
        if any(w in text_lower for w in ["debito", "débito", "debit"]):
            return "debit_card"
        if any(w in text_lower for w in ["transferencia", "transfer"]):
            return "transfer"
        return None

    def _extract_products(self, text: str) -> list:
        lines = text.strip().split("\n")
        products = []
        in_products = False
        product_pattern = re.compile(r"^(.+?)\s+\$?\s*(\d+(?:[.,]\d+)?)$")

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            lower = stripped.lower()
            if any(kw in lower for kw in ["total", "subtotal", "iva", "cambio", "efectivo", "gracias", "articulos", "artículos"]):
                if "total" in lower or "subtotal" in lower or "iva" in lower:
                    in_products = False
                continue
            if any(kw in lower for kw in ["cant.", "precio", "importe", "desc", "producto"]):
                in_products = True
                continue

            if not in_products:
                in_products = True

            m = product_pattern.search(stripped)
            if m:
                name = m.group(1).strip()
                try:
                    price = float(m.group(2).replace(",", ""))
                except ValueError:
                    continue
                category = self._classify_product(name)
                has_warranty = any(w in name.lower() for w in WARRANTY_KEYWORDS)
                products.append(OCRProduct(
                    name=name,
                    quantity=1,
                    unit="pza",
                    unit_price=price,
                    total_price=price,
                    category=category,
                    has_warranty=has_warranty,
                ))
            else:
                name = stripped
                category = self._classify_product(name)
                has_warranty = any(w in name.lower() for w in WARRANTY_KEYWORDS)
                products.append(OCRProduct(
                    name=name,
                    quantity=1,
                    unit="pza",
                    unit_price=0,
                    total_price=0,
                    category=category,
                    has_warranty=has_warranty,
                ))

        return products[:50]

    def _classify_product(self, name: str) -> str:
        name_lower = name.lower()
        for category, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in name_lower:
                    return CATEGORY_MAP.get(category, "otros")
        return "otros"

    def _check_warranty(self, products: list) -> bool:
        return any(p.has_warranty for p in products)

    def _estimate_confidence(self, text: str, products: list) -> float:
        if not text:
            return 0.0
        avg_line_len = sum(len(l) for l in text.split("\n") if l.strip()) / max(len([l for l in text.split("\n") if l.strip()]), 1)
        has_numbers = bool(re.search(r"\d+", text))
        has_prices = bool(re.search(r"\$\s*\d+", text))
        score = 0.3
        if avg_line_len > 20:
            score += 0.2
        if has_numbers:
            score += 0.2
        if has_prices:
            score += 0.2
        if products:
            score += 0.1
        return min(score, 1.0)
