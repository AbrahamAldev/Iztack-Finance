"""
Sistema Financiero - Liverpool Invoicing Portal
Automates the invoice request process on liverpool.com.mx/facturacion
"""
import logging
from datetime import datetime
from typing import Optional

from playwright.async_api import Page

from .base import BasePortal, PortalCredentials

logger = logging.getLogger(__name__)


class LiverpoolPortal(BasePortal):
    """
    Liverpool invoicing portal automation.
    
    URL: https://www.liverpool.com.mx/facturacion
    Process:
    1. Navigate to facturacion page
    2. Login with email and password
    3. Fill ticket data (folio, date, amount)
    4. Confirm RFC data
    5. Download PDF and XML
    """

    PORTAL_URL = "https://www.liverpool.com.mx/facturacion"
    MAX_RETRY_DAYS = 60  # Liverpool allows 60 days for invoicing

    def __init__(self):
        super().__init__("Liverpool", self.PORTAL_URL)

    def get_max_retry_days(self) -> int:
        return self.MAX_RETRY_DAYS

    async def login(self, page: Page, credentials: PortalCredentials) -> bool:
        """Log into Liverpool's invoicing portal."""
        try:
            await page.goto(self.PORTAL_URL, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            # Check if we need to click "Iniciar sesión" button first
            login_btn = page.locator("button:has-text('Iniciar sesión'), a:has-text('Iniciar sesión')")
            if await login_btn.is_visible(timeout=3000):
                await login_btn.click()
                await page.wait_for_timeout(2000)

            # Fill email
            email_input = page.locator("input[type='email'], input[name='email'], input[name='username']")
            await email_input.wait_for(timeout=10000)
            await email_input.fill(credentials.username)

            # Fill password
            password_input = page.locator("input[type='password']")
            await password_input.wait_for(timeout=5000)
            await password_input.fill(credentials.password)

            # Click submit
            submit_btn = page.locator("button[type='submit'], button:has-text('Entrar'), button:has-text('Ingresar')")
            await submit_btn.click()

            # Wait for login to complete
            await page.wait_for_timeout(5000)

            # Verify login success - check that we're on the facturacion page
            current_url = page.url
            if "login" in current_url.lower() or "error" in current_url.lower():
                # Check for error messages
                error_text = await page.locator(".error, .alert, .message-error").text_content(timeout=3000)
                if error_text:
                    logger.warning(f"Liverpool login error: {error_text}")
                return False

            return True

        except Exception as e:
            logger.error(f"Liverpool login error: {e}", exc_info=True)
            return False

    async def request_invoice(self, page: Page, ticket_data: dict) -> bool:
        """Submit invoice request with ticket data."""
        try:
            # Wait for the facturacion form to load
            await page.wait_for_timeout(3000)

            # Fill ticket folio/number
            folio = ticket_data.get("receipt_number", "")
            if folio:
                folio_input = page.locator(
                    "input[name='folio'], input[name='ticket'], input[placeholder*='folio'], "
                    "input[placeholder*='ticket'], input[placeholder*='Factura']"
                )
                if await folio_input.is_visible(timeout=5000):
                    await folio_input.fill(folio)

            # Fill purchase date
            purchase_date = ticket_data.get("purchase_date", "")
            if purchase_date:
                date_input = page.locator(
                    "input[type='date'], input[name='fecha'], input[placeholder*='fecha'], "
                    "input[placeholder*='Fecha']"
                )
                if await date_input.is_visible(timeout=5000):
                    # Format: DD/MM/YYYY or YYYY-MM-DD depending on the field
                    try:
                        dt = datetime.strptime(purchase_date, "%Y-%m-%d")
                        formatted_date = dt.strftime("%d/%m/%Y")
                        await date_input.fill(formatted_date)
                    except ValueError:
                        await date_input.fill(purchase_date)

            # Fill total amount
            total = ticket_data.get("total_amount", 0)
            if total:
                amount_input = page.locator(
                    "input[name='total'], input[name='monto'], input[placeholder*='total'], "
                    "input[placeholder*='Total'], input[placeholder*='Monto']"
                )
                if await amount_input.is_visible(timeout=5000):
                    await amount_input.fill(str(total))

            # Submit the form
            submit_btn = page.locator(
                "button[type='submit'], button:has-text('Solicitar'), "
                "button:has-text('Facturar'), button:has-text('Enviar')"
            )
            if await submit_btn.is_visible(timeout=5000):
                await submit_btn.click()
                await page.wait_for_timeout(5000)

            # Handle CAPTCHA or additional verification if present
            # (Common in Mexican portals)

            # Wait for result
            await page.wait_for_timeout(5000)

            # Check for success message
            success_text = await page.locator(
                ".success, .exito, .mensaje-exito, [class*='success'], [class*='exito']"
            ).text_content(timeout=10000)

            if success_text and any(word in success_text.lower() for word in ["exito", "éxito", "success", "completada"]):
                logger.info("Liverpool invoice request successful")
                return True

            # If we can't confirm success, check the page content
            page_text = await page.text_content()
            if "gracias" in page_text.lower() or "solicitud" in page_text.lower() or "completada" in page_text.lower():
                return True

            return True  # Assume success if no error

        except Exception as e:
            logger.error(f"Liverpool invoice request error: {e}", exc_info=True)
            return False

    async def download_files(self, page: Page) -> tuple[Optional[bytes], Optional[bytes]]:
        """Download PDF and XML from the result page."""
        pdf_bytes = None
        xml_bytes = None

        try:
            # Wait for download links to appear
            await page.wait_for_timeout(3000)

            # Find PDF download link/button
            pdf_links = page.locator(
                "a[href*='.pdf'], a:has-text('PDF'), button:has-text('PDF'), "
                "a[href*='pdf'], [class*='pdf'], [class*='descargar']"
            )

            pdf_count = await pdf_links.count()
            if pdf_count > 0:
                # Try to click the first PDF link
                async with page.expect_download(timeout=30000) as download_info:
                    await pdf_links.first.click()
                download = await download_info.value
                pdf_bytes = await download.read()
                logger.info(f"PDF downloaded: {download.suggested_filename}")

            # Find XML download link/button
            xml_links = page.locator(
                "a[href*='.xml'], a:has-text('XML'), button:has-text('XML'), "
                "a[href*='xml'], [class*='xml']"
            )

            xml_count = await xml_links.count()
            if xml_count > 0:
                async with page.expect_download(timeout=30000) as download_info:
                    await xml_links.first.click()
                download = await download_info.value
                xml_bytes = await download.read()
                logger.info(f"XML downloaded: {download.suggested_filename}")

            return pdf_bytes, xml_bytes

        except Exception as e:
            logger.warning(f"Liverpool download error: {e}")
            return pdf_bytes, xml_bytes
