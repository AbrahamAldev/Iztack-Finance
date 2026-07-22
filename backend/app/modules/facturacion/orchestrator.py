"""
Iztack-Finance - Facturación Orchestrator
Flujo completo de facturación inteligente post-OCR.
"""
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from app.database.models import Ticket, User, StoreCredential, Invoice
from app.modules.facturacion.portal_discovery import PortalDiscovery
from app.modules.facturacion.portal_learner import PortalLearner
from app.modules.facturacion.credential_manager import CredentialManager
from app.modules.facturacion.fiscal_advisor import FiscalAdvisor
from app.utils.llm import LLMClient

logger = logging.getLogger(__name__)


class InvoiceStep(Enum):
    """Steps in the billing workflow."""
    OCR_DONE = "ocr_done"
    DISCOVERING_URL = "discovering_url"
    ANALYZING_PORTAL = "analyzing_portal"
    NEED_CREDENTIALS = "need_credentials"
    NEED_FISCAL_DATA = "need_fiscal_data"
    NEED_GASTO_TYPE = "need_gasto_type"
    FILLING_FORM = "filling_form"
    SUBMITTING = "submitting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class InvoiceContext:
    """Context object passed through the billing workflow."""
    ticket: Ticket
    user: User
    portal_url: Optional[str] = None
    portal_type: str = "unknown"  # known, known_failed, unknown
    credentials: Optional[StoreCredential] = None
    fiscal_data: Dict[str, Any] = field(default_factory=dict)
    gasto_type: Optional[str] = None
    step: InvoiceStep = InvoiceStep.OCR_DONE
    error: Optional[str] = None
    needs_user_input: bool = False
    user_message: Optional[str] = None
    result: Optional[Invoice] = None


class FacturacionOrchestrator:
    """
    Orchestrates the entire billing workflow.
    
    Flow:
    1. Discover billing URL (ticket -> internet -> ask user)
    2. Analyze portal structure (Playwright + IA)
    3. Get/store credentials
    4. Get fiscal data
    5. Determine best 'gasto' type
    6. Fill and submit form
    """

    def __init__(self, llm_client: LLMClient, db):
        self.llm = llm_client
        self.db = db
        self.discovery = PortalDiscovery(llm_client)
        self.learner = PortalLearner(llm_client)
        self.credential_mgr = CredentialManager(db)
        self.fiscal_advisor = FiscalAdvisor(llm_client)

    async def start_invoicing(self, ticket: Ticket, user: User) -> InvoiceContext:
        """Start the billing workflow for a ticket."""
        ctx = InvoiceContext(ticket=ticket, user=user)
        logger.info(f"Starting billing for ticket {ticket.id} - store: {ticket.store_name}")
        return await self._continue_flow(ctx)

    async def _continue_flow(self, ctx: InvoiceContext) -> InvoiceContext:
        """Continue the billing workflow from current step."""
        
        # Step 1-2: Discover URL or analyze portal
        if ctx.step in (InvoiceStep.OCR_DONE, InvoiceStep.DISCOVERING_URL):
            ctx = await self._discover_and_analyze(ctx)
            if ctx.needs_user_input:
                return ctx

        # Step 3: Handle credentials
        if ctx.step == InvoiceStep.NEED_CREDENTIALS:
            ctx = await self._handle_credentials(ctx)
            if ctx.needs_user_input:
                return ctx

        # Step 4: Get fiscal data
        if ctx.step == InvoiceStep.NEED_FISCAL_DATA:
            ctx = await self._handle_fiscal_data(ctx)
            if ctx.needs_user_input:
                return ctx

        # Step 5: Determine gasto type
        if ctx.step == InvoiceStep.NEED_GASTO_TYPE:
            ctx = await self._handle_gasto_type(ctx)
            if ctx.needs_user_input:
                return ctx

        # Step 6-7: Fill and submit
        if ctx.step == InvoiceStep.FILLING_FORM:
            ctx = await self._fill_and_submit(ctx)

        return ctx

    async def _discover_and_analyze(self, ctx: InvoiceContext) -> InvoiceContext:
        """Discover billing URL and analyze portal structure."""
        ctx.step = InvoiceStep.DISCOVERING_URL
        
        # Try to find URL from known portals first
        portal_url = await self.discovery.find_portal_url(
            store_name=ctx.ticket.store_name,
            store_category=ctx.ticket.store_category,
            ocr_text=ctx.ticket.ocr_raw_text,
        )

        if portal_url:
            ctx.portal_url = portal_url
            ctx.portal_type = "known"
        else:
            # Try to discover via IA + internet search
            discovery_result = await self.discovery.discover_unknown_portal(
                store_name=ctx.ticket.store_name,
                ocr_text=ctx.ticket.ocr_raw_text,
            )
            if discovery_result.get("url"):
                ctx.portal_url = discovery_result["url"]
                ctx.portal_type = "unknown"
            elif discovery_result.get("not_found"):
                ctx.step = InvoiceStep.FAILED
                ctx.error = f"No se encontró página de facturación para {ctx.ticket.store_name}"
                ctx.needs_user_input = True
                ctx.user_message = (
                    f"❌ No encontré la página de facturación para *{ctx.ticket.store_name}*.\n\n"
                    "¿Sabes cuál es la URL de facturación de esta tienda? "
                    "Escríbela y la registraré para futuros tickets."
                )
                return ctx

        # Analyze portal structure
        ctx.step = InvoiceStep.ANALYZING_PORTAL
        structure = await self.learner.analyze_portal(ctx.portal_url, ctx.ticket.store_name)
        
        if structure.get("requires_login"):
            ctx.step = InvoiceStep.NEED_CREDENTIALS
        elif structure.get("requires_fiscal_data"):
            ctx.step = InvoiceStep.NEED_FISCAL_DATA
        else:
            ctx.step = InvoiceStep.FILLING_FORM

        return ctx

    async def _handle_credentials(self, ctx: InvoiceContext) -> InvoiceContext:
        """Get or create credentials for the portal."""
        existing = await self.credential_mgr.get_credentials(
            ctx.user.id, ctx.ticket.store_name
        )
        
        if existing and existing.has_account:
            ctx.credentials = existing
            ctx.step = InvoiceStep.FILLING_FORM
            return ctx

        # Need to create account
        ctx.needs_user_input = True
        ctx.user_message = (
            f"🔐 *{ctx.ticket.store_name}* requiere cuenta para facturar.\n\n"
            "¿Quieres que cree una cuenta automáticamente?\n"
            f"• Usaré tu email *{ctx.user.email}*\n"
            "• Generaré una contraseña segura\n"
            "• Te daré las credenciales para que las guardes\n\n"
            "Responde *SÍ* para crear la cuenta automáticamente, "
            "o *NO* si prefieres darme una cuenta existente."
        )
        return ctx

    async def _handle_fiscal_data(self, ctx: InvoiceContext) -> InvoiceContext:
        """Get fiscal data needed for billing."""
        ctx.fiscal_data = await self.fiscal_advisor.get_user_fiscal_data(ctx.user.id)
        
        # Check if we have all required fields
        required = ["rfc", "razon_social", "codigo_postal", "regimen_fiscal"]
        missing = [f for f in required if not ctx.fiscal_data.get(f)]
        
        if missing:
            ctx.needs_user_input = True
            ctx.user_message = (
                f"📋 Necesito algunos datos fiscales para facturar en *{ctx.ticket.store_name}*:\n\n"
                f"• {', '.join(missing).replace('_', ' ').title()}\n\n"
                "Puedes:\n"
                "1. Decírmelos aquí mismo y los guardo para futuras facturas\n"
                "2. Subir tu *Constancia de Situación Fiscal* (PDF) y los extraigo automáticamente"
            )
            return ctx
        
        ctx.step = InvoiceStep.NEED_GASTO_TYPE
        return ctx

    async def _handle_gasto_type(self, ctx: InvoiceContext) -> InvoiceContext:
        """Determine the best gasto type based on products and fiscal regime."""
        product_categories = []
        if ctx.ticket.products:
            product_categories = [
                p.category for p in ctx.ticket.products if p.category
            ]

        recommendation = await self.fiscal_advisor.recommend_gasto_type(
            regimen=ctx.fiscal_data.get("regimen_fiscal", ""),
            products=product_categories,
            store_name=ctx.ticket.store_name,
        )

        if recommendation.get("auto"):
            # AI is confident, use recommendation
            ctx.gasto_type = recommendation["gasto_type"]
            ctx.step = InvoiceStep.FILLING_FORM
        else:
            # Need user confirmation
            ctx.needs_user_input = True
            ctx.user_message = (
                f"📊 Según tu régimen fiscal y los productos comprados, "
                f"te recomiendo facturar como:\n\n"
                f"*{recommendation['gasto_type']}*\n\n"
                f"📝 *Motivo:* {recommendation['reason']}\n\n"
                "¿Estás de acuerdo? Responde *SÍ* para usar este tipo de gasto, "
                "o dime cuál prefieres."
            )
        return ctx

    async def _fill_and_submit(self, ctx: InvoiceContext) -> InvoiceContext:
        """Fill the billing form and submit."""
        ctx.step = InvoiceStep.SUBMITTING
        
        try:
            result = await self.learner.fill_and_submit(
                portal_url=ctx.portal_url,
                ticket=ctx.ticket,
                credentials=ctx.credentials,
                fiscal_data=ctx.fiscal_data,
                gasto_type=ctx.gasto_type,
            )
            
            if result.get("success"):
                ctx.step = InvoiceStep.COMPLETED
                ctx.result = result.get("invoice")
            else:
                ctx.step = InvoiceStep.FAILED
                ctx.error = result.get("error", "Error desconocido al facturar")
                ctx.needs_user_input = True
                ctx.user_message = (
                    f"❌ No se pudo facturar en *{ctx.ticket.store_name}*.\n\n"
                    f"Error: {ctx.error}"
                )
        except Exception as e:
            logger.error(f"Billing form fill error: {e}", exc_info=True)
            ctx.step = InvoiceStep.FAILED
            ctx.error = str(e)
            ctx.needs_user_input = True
            ctx.user_message = (
                f"❌ Error inesperado al facturar en *{ctx.ticket.store_name}*.\n\n"
                "Se registró el error. Intenta de nuevo más tarde."
            )

        return ctx

    async def handle_user_response(
        self, ctx: InvoiceContext, user_response: str
    ) -> InvoiceContext:
        """Handle user's response to a question and continue the flow."""
        response_lower = user_response.lower().strip()

        if ctx.step == InvoiceStep.NEED_CREDENTIALS:
            if response_lower in ("sí", "si", "yes", "ok", "dale"):
                ctx = await self.credential_mgr.create_account(
                    ctx.user.id, ctx.ticket.store_name, ctx.user.email
                )
                ctx.step = InvoiceStep.FILLING_FORM
                ctx.needs_user_input = True
                ctx.user_message = (
                    f"✅ *Cuenta creada en {ctx.ticket.store_name}*\n\n"
                    f"📧 Usuario: *{ctx.user.email}*\n"
                    f"🔑 Contraseña: *{ctx.credentials.credential_hint}*\n\n"
                    "Guarda estas credenciales. Continuaré con la facturación..."
                )
            else:
                ctx.needs_user_input = True
                ctx.user_message = (
                    "Por favor, dime el *usuario* y *contraseña* "
                    "de tu cuenta de facturación en este formato:\n\n"
                    "`usuario@email.com | contraseña`"
                )

        elif ctx.step == InvoiceStep.NEED_GASTO_TYPE:
            if response_lower in ("sí", "si", "yes", "ok"):
                ctx.step = InvoiceStep.FILLING_FORM
            else:
                ctx.gasto_type = user_response.strip()
                ctx.step = InvoiceStep.FILLING_FORM

        elif ctx.step == InvoiceStep.FAILED:
            if "http" in response_lower:
                ctx.portal_url = response_lower.strip()
                ctx.portal_type = "user_provided"
                ctx.step = InvoiceStep.ANALYZING_PORTAL
                ctx.needs_user_input = False

        # Continue the flow
        return await self._continue_flow(ctx)