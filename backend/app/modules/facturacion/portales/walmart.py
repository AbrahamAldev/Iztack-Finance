"""
Sistema Financiero - Walmart Mexico Invoicing Portal
"""
import logging
from datetime import datetime
from typing import Optional

from playwright.async_api import Page

from .base import BasePortal, PortalCredentials

logger = logging.getLogger(__name__)


class WalmartPortal(BasePortal):
    """Walmart Mexico invoicing portal automation."""

    PORTAL_URL = "https://www.walmart.com.mx/facturacion"
    MAX_RETRY_DAYS = 60

    def __init__(self):
        super().__init__("Walmart", self.PORTAL_URL)

    def get_max_retry_days(self) -> int:
        return self.MAX_RETRY_DAYS

    async def login(self, page: Page, credentials: PortalCredentials) -> bool:
        try:
            await page.goto(self.PORTAL_URL, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            # Click "Iniciar sesión" if needed
            login_btn = page.locator("button:has-text('Iniciar sesión'), a:has-text('Iniciar sesión'), button:has-text('Ingresar')")
            if await login_btn.is_visible(timeout=3000):
                await login_btn.click()
                await page.wait_for_timeout(2000)

            # Fill email
            email_input = page.locator("input[type='email'], input[name='email'], input[name='username']")
            if await email_input.is_visible(timeout=5000):
                await email_input.fill(credentials.username)

            # Fill password
            password_input = page.locator("input[type='password']")
            if await password_input.is_visible(timeout=5000):
                await password_input.fill(credentials.password)

            # Submit
            submit_btn = page.locator("button[type='submit'], button:has-text('Entrar'), button:has-text('Ingresar')")
            if await submit_btn.is_visible(timeout=5000):
                await submit_btn.click()
                await page.wait_for_timeout(5000)

            return True
        except Exception as e:
            logger.error(f"Walmart login error: {e}", exc_info=True)
            return False

    async def request_invoice(self, page: Page, ticket_data: dict) -> bool:
        try:
            await page.wait_for_timeout(3000)

            # Fill ticket number / order ID
            ticket = ticket_data.get("receipt_number", "")
            if ticket:
                input_field = page.locator("input[name*='ticket'], input[name*='folio'], input[placeholder*='ticket'], input[placeholder*='folio']")
                if await input_field.is_visible(timeout=5000):
                    await input_field.fill(ticket)

            # Fill date
            purchase_date = ticket_data.get("purchase_date", "")
            if purchase_date:
                date_input = page.locator("input[type='date'], input[name*='fecha'], input[placeholder*='fecha']")
                if await date_input.is_visible(timeout=5000):
                    try:
                        dt = datetime.strptime(purchase_date, "%Y-%m-%d")
                        await date_input.fill(dt.strftime("%d/%m/%Y"))
                    except ValueError:
                        await date_input.fill(purchase_date)

            # Fill total
            total = ticket_data.get("total_amount", 0)
            if total:
                amount_input = page.locator("input[name*='total'], input[name*='monto'], input[placeholder*='total']")
                if await amount_input.is_visible(timeout=5000):
                    await amount_input.fill(str(total))

            # Fill RFC
            rfc = ticket_data.get("rfc", "")
            if rfc:
                rfc_input = page.locator("input[name*='rfc'], input[placeholder*='RFC']")
                if await rfc_input.is_visible(timeout=5000):
                    await rfc_input.fill(rfc)

            # Submit
            submit_btn = page.locator("button[type='submit'], button:has-text('Solicitar'), button:has-text('Facturar')")
            if await submit_btn.is_visible(timeout=5000):
                await submit_btn.click()
                await page.wait_for_timeout(5000)

            return True
        except Exception as e:
            logger.error(f"Walmart invoice request error: {e}", exc_info=True)
            return False

    async def download_files(self, page: Page) -> tuple[Optional[bytes], Optional[bytes]]:
        pdf_bytes = None
        xml_bytes = None
        try:
            await page.wait_for_timeout(3000)

            pdf_links = page.locator("a[href*='.pdf'], a:has-text('PDF'), button:has-text('PDF')")
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
            logger.warning(f"Walmart download error: {e}")

        return pdf_bytes, xml_bytes
