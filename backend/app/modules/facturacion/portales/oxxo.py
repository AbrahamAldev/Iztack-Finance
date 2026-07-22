"""
Sistema Financiero - Oxxo Invoicing Portal
Oxxo uses a generic CFDI portal for all their stores.
"""
import logging

from playwright.async_api import Page
from .base import BasePortal, PortalCredentials

logger = logging.getLogger(__name__)


class OxxoPortal(BasePortal):
    """Oxxo invoicing portal (via femsa.com.mx/facturacion)."""

    PORTAL_URL = "https://www.femsa.com.mx/facturacion"
    MAX_RETRY_DAYS = 30

    def __init__(self):
        super().__init__("Oxxo", self.PORTAL_URL)

    def get_max_retry_days(self) -> int:
        return self.MAX_RETRY_DAYS

    async def login(self, page: Page, credentials: PortalCredentials) -> bool:
        try:
            await page.goto(self.PORTAL_URL, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
            # Oxxo's portal typically doesn't require login
            return True
        except Exception as e:
            logger.error(f"Oxxo error: {e}", exc_info=True)
            return False

    async def request_invoice(self, page: Page, ticket_data: dict) -> bool:
        try:
            await page.wait_for_timeout(3000)
            
            ticket = ticket_data.get("receipt_number", "")
            if ticket:
                inp = page.locator("input[name*='folio'], input[name*='ticket'], input[placeholder*='folio'], input[placeholder*='ticket']")
                if await inp.is_visible(timeout=5000):
                    await inp.fill(ticket)
            
            date_str = ticket_data.get("purchase_date", "")
            if date_str:
                inp = page.locator("input[type='date'], input[name*='fecha']")
                if await inp.is_visible(timeout=5000):
                    await inp.fill(date_str)
            
            total = ticket_data.get("total_amount", 0)
            if total:
                inp = page.locator("input[name*='total'], input[name*='monto']")
                if await inp.is_visible(timeout=5000):
                    await inp.fill(str(total))
            
            submit_btn = page.locator("button[type='submit'], button:has-text('Facturar')")
            if await submit_btn.is_visible(timeout=5000):
                await submit_btn.click()
                await page.wait_for_timeout(5000)
            
            return True
        except Exception as e:
            logger.error(f"Oxxo invoice error: {e}", exc_info=True)
            return False

    async def download_files(self, page: Page) -> tuple:
        pdf_bytes = xml_bytes = None
        try:
            await page.wait_for_timeout(3000)
            for ext, label in [(".pdf", "PDF"), (".xml", "XML")]:
                links = page.locator(f"a[href*='{ext}'], a:has-text('{label}')")
                if await links.count() > 0:
                    async with page.expect_download(timeout=30000) as info:
                        await links.first.click()
                    d = await info.value
                    data = await d.read()
                    if ext == ".pdf":
                        pdf_bytes = data
                    else:
                        xml_bytes = data
        except Exception as e:
            logger.warning(f"Oxxo download error: {e}")
        return pdf_bytes, xml_bytes