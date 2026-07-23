"""
Sistema Financiero - IKEA Mexico Invoicing Portal
"""
import logging
from datetime import datetime
from typing import Optional

from playwright.async_api import Page

from .base import BasePortal, PortalCredentials

logger = logging.getLogger(__name__)


class IKEAPortal(BasePortal):
    """IKEA Mexico invoicing portal automation."""

    PORTAL_URL = "https://www.ikea.com/mx/es/customer-service/facturacion/"
    MAX_RETRY_DAYS = 30

    def __init__(self):
        super().__init__("IKEA", self.PORTAL_URL)

    def get_max_retry_days(self) -> int:
        return self.MAX_RETRY_DAYS

    async def login(self, page: Page, credentials: PortalCredentials) -> bool:
        try:
            await page.goto(self.PORTAL_URL, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
            # IKEA doesn't require login for invoice requests
            return True
        except Exception as e:
            logger.error(f"IKEA portal error: {e}", exc_info=True)
            return False

    async def request_invoice(self, page: Page, ticket_data: dict) -> bool:
        try:
            await page.wait_for_timeout(3000)

            # Fill folio / order number
            order_number = ticket_data.get("receipt_number", "")
            if order_number:
                order_input = page.locator(
                    "input[name*='order'], input[name*='pedido'], input[placeholder*='pedido'], "
                    "input[placeholder*='orden'], input[placeholder*='Order']"
                )
                if await order_input.is_visible(timeout=5000):
                    await order_input.fill(order_number)

            # Fill date
            purchase_date = ticket_data.get("purchase_date", "")
            if purchase_date:
                date_input = page.locator(
                    "input[type='date'], input[name*='fecha'], input[placeholder*='fecha'], "
                    "input[placeholder*='Date']"
                )
                if await date_input.is_visible(timeout=5000):
                    try:
                        dt = datetime.strptime(purchase_date, "%Y-%m-%d")
                        await date_input.fill(dt.strftime("%Y-%m-%d"))
                    except ValueError:
                        await date_input.fill(purchase_date)

            # Fill total
            total = ticket_data.get("total_amount", 0)
            if total:
                amount_input = page.locator(
                    "input[name*='total'], input[name*='monto'], input[placeholder*='total']"
                )
                if await amount_input.is_visible(timeout=5000):
                    await amount_input.fill(str(total))

            # RFC
            rfc = ticket_data.get("rfc", "")
            if rfc:
                rfc_input = page.locator(
                    "input[name*='rfc'], input[placeholder*='RFC'], input[name*='tax']"
                )
                if await rfc_input.is_visible(timeout=5000):
                    await rfc_input.fill(rfc)

            # Submit
            submit_btn = page.locator(
                "button[type='submit'], button:has-text('Solicitar'), "
                "button:has-text('Facturar'), button:has-text('Enviar')"
            )
            if await submit_btn.is_visible(timeout=5000):
                await submit_btn.click()
                await page.wait_for_timeout(5000)

            return True

        except Exception as e:
            logger.error(f"IKEA invoice request error: {e}", exc_info=True)
            return False

    async def download_files(self, page: Page) -> tuple[Optional[bytes], Optional[bytes]]:
        pdf_bytes = None
        xml_bytes = None
        try:
            await page.wait_for_timeout(3000)

            pdf_links = page.locator(
                "a[href*='.pdf'], a:has-text('PDF'), button:has-text('PDF')"
            )
            if await pdf_links.count() > 0:
                async with page.expect_download(timeout=30000) as download_info:
                    await pdf_links.first.click()
                download = await download_info.value
                pdf_bytes = await download.read()

            xml_links = page.locator(
                "a[href*='.xml'], a:has-text('XML'), button:has-text('XML')"
            )
            if await xml_links.count() > 0:
                async with page.expect_download(timeout=30000) as download_info:
                    await xml_links.first.click()
                download = await download_info.value
                xml_bytes = await download.read()

        except Exception as e:
            logger.warning(f"IKEA download error: {e}")

        return pdf_bytes, xml_bytes
