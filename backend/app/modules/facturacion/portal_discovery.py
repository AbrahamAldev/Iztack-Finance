"""
Iztack-Finance - Portal Discovery
Finds billing portal URLs for stores.
"""
import logging
from typing import Dict, Optional

from app.utils.llm import LLMClient

logger = logging.getLogger(__name__)

# Known billing portal URLs
KNOWN_PORTALS = {
    "liverpool": "https://www.liverpool.com.mx/facturacion",
    "ikea": "https://www.ikea.com/mx/es/customer-service/facturacion/",
    "walmart": "https://www.walmart.com.mx/facturacion",
    "amazon": "https://www.amazon.com.mx/gp/b2b/invoice",
    "home_depot": "https://www.homedepot.com.mx/facturacion",
    "oxxo": "https://www.oxxo.com/facturacion",
    "pemex": "https://www.pemex.com/facturacion",
    "costco": "https://www.costco.com.mx/facturacion",
    "sams_club": "https://www.sams.com.mx/facturacion",
    "soriana": "https://www.soriana.com/facturacion",
    "chedraui": "https://www.chedraui.com.mx/facturacion",
    "farmacias_similares": "https://www.farmaciasdesimilares.com.mx/facturacion",
}


class PortalDiscovery:
    """Discovers billing portal URLs for stores."""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def find_portal_url(
        self, store_name: str, store_category: Optional[str] = None, ocr_text: Optional[str] = None
    ) -> Optional[str]:
        """Find billing URL for a store."""
        # Check known portals
        if store_category and store_category in KNOWN_PORTALS:
            return KNOWN_PORTALS[store_category]

        # Check by name
        name_lower = store_name.lower().strip()
        for key, url in KNOWN_PORTALS.items():
            if key in name_lower or name_lower in key:
                return url

        return None

    async def discover_unknown_portal(
        self, store_name: str, ocr_text: Optional[str] = None
    ) -> Dict:
        """Try to discover billing URL for an unknown store."""
        # Search in OCR text
        if ocr_text:
            import re
            urls = re.findall(r"https?://[^\s]+factur[^\s]*", ocr_text, re.IGNORECASE)
            if urls:
                return {"url": urls[0], "source": "ticket"}

        # Try LLM search
        try:
            response = await self.llm.chat(
                user_message=f"¿Cuál es la URL oficial de facturación de {store_name}? Responde SOLO con la URL.",
                max_tokens=100,
                temperature=0.0,
            )
            import re
            urls = re.findall(r"https?://[^\s]+", response)
            if urls:
                return {"url": urls[0], "source": "llm"}
        except Exception:
            pass

        return {"not_found": True}
