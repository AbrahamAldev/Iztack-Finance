"""
Sistema Financiero - Base Portal
Abstract base class for all store invoicing portals.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
from datetime import date
import logging

from playwright.async_api import async_playwright, Page, Browser

logger = logging.getLogger(__name__)


@dataclass
class PortalCredentials:
    """Credentials for accessing a store's invoicing portal."""
    username: str
    password: str
    rfc: str  # Mexican tax ID
    email: str


@dataclass
class InvoiceResult:
    """Result of an invoice request."""
    success: bool
    pdf_url: Optional[str] = None
    pdf_bytes: Optional[bytes] = None
    xml_url: Optional[str] = None
    xml_bytes: Optional[bytes] = None
    invoice_uuid: Optional[str] = None  # CFDI UUID
    error_message: Optional[str] = None
    found_in_email: bool = False


class BasePortal(ABC):
    """
    Abstract base class for store invoicing portals.
    
    Each store portal must implement:
    - portal_url: The URL of the invoicing page
    - login(): Navigate and log into the portal
    - request_invoice(): Submit the invoice request
    - download_files(): Download PDF and XML
    """

    def __init__(self, store_name: str, portal_url: str):
        self.store_name = store_name
        self.portal_url = portal_url
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.credentials: Optional[PortalCredentials] = None

    @abstractmethod
    async def login(self, page: Page, credentials: PortalCredentials) -> bool:
        """Log into the store's invoicing portal."""
        pass

    @abstractmethod
    async def request_invoice(self, page: Page, ticket_data: dict) -> bool:
        """
        Submit the invoice request with ticket data.
        
        Args:
            page: Playwright page object
            ticket_data: Dict with at least:
                - receipt_number: str
                - purchase_date: str (YYYY-MM-DD)
                - total_amount: float
                - store_name: str
        """
        pass

    @abstractmethod
    async def download_files(self, page: Page) -> tuple[Optional[bytes], Optional[bytes]]:
        """
        Download PDF and XML files.
        Returns: (pdf_bytes, xml_bytes)
        """
        pass

    async def get_max_retry_days(self) -> int:
        """
        Get maximum days after purchase that invoicing is allowed.
        In Mexico, typically 30-60 days depending on the store.
        """
        return 60

    async def run(self, credentials: PortalCredentials, ticket_data: dict) -> InvoiceResult:
        """
        Execute the full invoice request flow.
        
        Args:
            credentials: Portal login credentials
            ticket_data: Ticket information for the invoice request
            
        Returns:
            InvoiceResult with success status and file data
        """
        self.credentials = credentials
        result = InvoiceResult(success=False)
        
        try:
            async with async_playwright() as pw:
                # Launch browser
                self.browser = await pw.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                    ]
                )
                
                context = await self.browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/125.0.0.0 Safari/537.36"
                    ),
                    locale="es-MX",
                    timezone_id="America/Mexico_City",
                )
                
                self.page = await context.new_page()
                
                # Step 1: Login
                logger.info(f"[{self.store_name}] Iniciando sesión en {self.portal_url}")
                login_success = await self.login(self.page, credentials)
                
                if not login_success:
                    result.error_message = f"Error al iniciar sesión en {self.store_name}"
                    return result
                
                logger.info(f"[{self.store_name}] Login exitoso")
                
                # Step 2: Request invoice
                logger.info(f"[{self.store_name}] Solicitando factura...")
                request_success = await self.request_invoice(self.page, ticket_data)
                
                if not request_success:
                    result.error_message = f"Error al solicitar factura en {self.store_name}"
                    return result
                
                logger.info(f"[{self.store_name}] Factura solicitada exitosamente")
                
                # Step 3: Download files
                logger.info(f"[{self.store_name}] Descargando archivos...")
                pdf_bytes, xml_bytes = await self.download_files(self.page)
                
                result.success = True
                result.pdf_bytes = pdf_bytes
                result.xml_bytes = xml_bytes
                
                logger.info(f"[{self.store_name}] Proceso completado exitosamente")
                
        except Exception as e:
            logger.error(f"[{self.store_name}] Error: {e}", exc_info=True)
            result.error_message = f"Error en {self.store_name}: {str(e)}"
        
        finally:
            if self.browser:
                await self.browser.close()
        
        return result

    async def take_screenshot(self, name: str = "debug"):
        """Take a screenshot for debugging purposes."""
        if self.page:
            await self.page.screenshot(path=f"/tmp/{self.store_name}_{name}.png", full_page=True)

    async def fill_input(self, selector: str, value: str, timeout: int = 10000):
        """Safely fill an input field."""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            await self.page.fill(selector, value)
            return True
        except Exception as e:
            logger.warning(f"[{self.store_name}] Error filling {selector}: {e}")
            return False

    async def click_button(self, selector: str, timeout: int = 10000):
        """Safely click a button."""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            await self.page.click(selector)
            return True
        except Exception as e:
            logger.warning(f"[{self.store_name}] Error clicking {selector}: {e}")
            return False

    async def wait_for_navigation(self, timeout: int = 30000):
        """Wait for page navigation to complete."""
        try:
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
            return True
        except Exception:
            return False