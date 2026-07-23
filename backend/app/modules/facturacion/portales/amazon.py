"""
Sistema Financiero - Amazon Mexico Invoicing Portal
"""
import logging
from typing import Optional

from playwright.async_api import Page

from .base import BasePortal, PortalCredentials

logger = logging.getLogger(__name__)


class AmazonPortal(BasePortal):
    """Amazon Mexico invoicing portal automation."""

    PORTAL_URL = "https://www.amazon.com.mx/facturacion"
    MAX_RETRY_DAYS = 90  # Amazon allows up to 90 days

    def __init__(self):
        super().__init__("Amazon", self.PORTAL_URL)

    def get_max_retry_days(self) -> int:
        return self.MAX_RETRY_DAYS

    async def login(self, page: Page, credentials: PortalCredentials) -> bool:
        try:
            await page.goto(self.PORTAL_URL, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            # Amazon may redirect to login
            email_input = page.locator("input[type='email'], input[name='email']")
            if await email_input.is_visible(timeout=5000):
                await email_input.fill(credentials.username)
                submit_btn = page.locator("input[type='submit'], button[type='submit'], #continue")
                if await submit_btn.is_visible(timeout=3000):
                    await submit_btn.click()
                    await page.wait_for_timeout(2000)

                # Password
                password_input = page.locator("input[type='password']")
                if await password_input.is_visible(timeout=5000):
                    await password_input.fill(credentials.password)
                    signin_btn = page.locator("input[type='submit'], #signInSubmit")
                    if await signin_btn.is_visible(timeout=3000):
                        await signin_btn.click()
                        await page.wait_for_timeout(5000)

            return True
        except Exception as e:
            logger.error(f"Amazon login error: {e}", exc_info=True)
            return False

    async def request_invoice(self, page: Page, ticket_data: dict) -> bool:
        try:
            await page.wait_for_timeout(3000)

            # Amazon typically uses Order ID
            order_id = ticket_data.get("receipt_number", "")
            if order_id:
                order_input = page.locator("input[name*='order'], input[name*='pedido'], input[placeholder*='order'], input[placeholder*='Order']")
                if await order_input.is_visible(timeout=5000):
                    await order_input.fill(order_id)

            # RFC
            rfc = ticket_data.get("rfc", "")
            if rfc:
                rfc_input = page.locator("input[name*='rfc'], input[placeholder*='RFC']")
                if await rfc_input.is_visible(timeout=5000):
                    await rfc_input.fill(rfc)

            # Submit
            submit_btn = page.locator("button[type='submit'], a:has-text('Solicitar'), button:has-text('Facturar')")
            if await submit_btn.is_visible(timeout=5000):
                await submit_btn.click()
                await page.wait_for_timeout(5000)

            return True
        except Exception as e:
            logger.error(f"Amazon invoice request error: {e}", exc_info=True)
            return False

    async def download_files(self, page: Page) -> tuple[Optional[bytes], Optional[bytes]]:
        pdf_bytes = None
        xml_bytes = None
        try:
            await page.wait_for_timeout(3000)

            pdf_links = page.locator("a[href*='.pdf'], a:has-text('PDF'), button:has-text('PDF'), a:has-text('Descargar PDF')")
            if await pdf_links.count() > 0:
                async with page.expect_download(timeout=30000) as info:
                    await pdf_links.first.click()
                download = await info.value
                pdf_bytes = await download.read()

            xml_links = page.locator("a[href*='.xml'], a:has-text('XML'), button:has-text('XML')")
            if await xml_links.count() > 0:
                async with page.expect_download(timeout=30000) as info:
                    await xml_links.first.click()
                download = await info.value
                xml_bytes = await download.read()

        except Exception as e:
            logger.warning(f"Amazon download error: {e}")

        return pdf_bytes, xml_bytes
