"""
Iztack-Finance - Chat Service
In-app chat with AI responses via OpenRouter (DeepSeek).
Security: prompt injection protection, data isolation per user.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import json

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, ChatMessage, Ticket, Product, Invoice, ShoppingList
from app.modules.auth.service import AuthService
from app.modules.ocr.service import OCRService
from app.modules.ocr.schemas import OCRResponse
from app.utils.llm import LLMClient

logger = logging.getLogger(__name__)


class ChatService:
    """Chat service with AI (OpenRouter) and security measures."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ocr_service = OCRService()
        # LLM client will be initialized when a message needs AI
        self._llm: Optional[LLMClient] = None

    def _get_llm(self) -> Optional[LLMClient]:
        """Get or initialize LLM client with the stored API key."""
        if self._llm:
            return self._llm
        # Try to get API key from settings
        import os
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if api_key and LLMClient.validate_api_key(api_key):
            self._llm = LLMClient(api_key)
            return self._llm
        return None

    async def process_message(
        self, user_id: str, text: str = None, image_bytes: bytes = None
    ) -> Tuple[str, dict]:
        """Process a chat message with AI."""
        # Save user message
        if text:
            await self._save_message(user_id, "user", text, "text")

        # If there's an image, process as ticket first
        if image_bytes:
            return await self._handle_ticket_image(user_id, image_bytes)

        # If only text, route to AI or commands
        if not text:
            return "Envía una foto de tu ticket o escribe un mensaje.", {}

        return await self._handle_text_message(user_id, text)

    async def _handle_ticket_image(
        self, user_id: str, image_bytes: bytes
    ) -> Tuple[str, dict]:
        """Process a ticket image with OCR and return AI-formatted result."""
        await self._save_message(user_id, "bot", "📸 Procesando imagen...", "status")

        import os
        try:
            # 🔍 SENSOR 1-3: Reception → Preprocess → OCR
            from app.modules.tickets.tracer import trace_step
            trace_step(user_id, "reception", status="ok", details={"size_bytes": len(image_bytes)})
            trace_step(user_id, "preprocess", status="ok")
            result: OCRResponse = self.ocr_service.extract_from_image(image_bytes)
            trace_step(user_id, "ocr", status="ok" if result.success else "error",
                       details={"confidence": result.data.confidence if result.data else None,
                                "store_name": result.data.store_name if result.data else None})

            if not result.success:
                response = (
                    "❌ No se pudo leer el ticket.\n\n"
                    f"{result.error}\n\n"
                    "💡 Sugerencias:\n"
                    "• Asegúrate de buena iluminación\n"
                    "• Coloca el ticket sobre una superficie plana\n"
                    "• Evita sombras y reflejos\n"
                    "• Si el ticket es muy largo, toma 2 fotos como continuación"
                )
                await self._save_message(user_id, "bot", response, "error")
                return response, {"type": "error"}

            data = result.data
            lines = [f"✅ Ticket identificado", ""]

            if data.store_name:
                lines.append(f"🏪 Tienda: **{data.store_name}**")
            if data.purchase_date:
                lines.append(f"📅 Fecha: {data.purchase_date.strftime('%d/%m/%Y')}")
            if data.total_amount:
                lines.append(f"💰 Total: **${data.total_amount:,.2f}**")
            if data.payment_method:
                lines.append(f"💳 Pago: {data.payment_method}")

            lines.append("")

            if data.products:
                lines.append("📦 Productos:")
                for i, p in enumerate(data.products[:5], 1):
                    line = f"{i}. {p.name}"
                    if p.quantity and p.quantity > 1:
                        line += f" x{p.quantity}"
                    if p.total_price:
                        line += f" = ${p.total_price:,.2f}"
                    lines.append(line)
                if len(data.products) > 5:
                    lines.append(f"... y {len(data.products) - 5} más")

            lines.append("")
            lines.append("🔄 Iniciando facturación automática...")

            # 🔥 INTEGRACIÓN: Disparar facturación post-OCR
            try:
                api_key = os.environ.get("OPENROUTER_API_KEY", "")
                if api_key:
                    from app.modules.tickets.billing import trigger_billing
                    from app.database.connection import get_db_sync
                    db_sync = get_db_sync()
                    billing_ctx = await trigger_billing(data, user_id, db_sync)
                    if billing_ctx:
                        lines.append("")
                        lines.append(f"📋 Facturación: {billing_ctx.step.value}")
                        if billing_ctx.needs_user_input:
                            lines.append(f"💬 {billing_ctx.user_message[:200]}")
                    db_sync.close()
            except Exception as billing_err:
                logger.error(f"Billing trigger failed: {billing_err}")
                lines.append("⚠️ La facturación automática falló. Puedes intentarlo manualmente.")

            if data.has_warranty_items:
                lines.append("🔧 ¡Producto con garantía detectado! Se archivará en garantías.")

            response = "\n".join(lines)
            metadata = {
                "type": "ticket",
                "store_name": data.store_name,
                "total_amount": data.total_amount,
                "has_warranty": data.has_warranty_items,
                "product_count": len(data.products) if data.products else 0,
            }

            await self._save_message(user_id, "bot", response, "ticket_result")
            return response, metadata

        except Exception as e:
            logger.error(f"Chat image error: {e}", exc_info=True)
            error_msg = "❌ Error al procesar la imagen. Intenta de nuevo."
            await self._save_message(user_id, "bot", error_msg, "error")
            return error_msg, {"type": "error"}

    async def _handle_text_message(
        self, user_id: str, text: str
    ) -> Tuple[str, dict]:
        """Route text to AI or handle simple commands locally."""
        lower = text.lower().strip()

        # Handle commands locally (no AI needed)
        if lower in ("/start",):
            response = (
                "¡Hola! 👋 Soy tu asistente financiero Iztack.\n\n"
                "Puedes:\n"
                "📸 Enviarme fotos de tickets\n"
                "📊 Preguntar sobre tus finanzas\n"
                "🛒 Consultar tu lista de compras\n"
                "🔧 Buscar garantías\n\n"
                "Escribe /ayuda para ver todos los comandos."
            )
            await self._save_message(user_id, "bot", response, "text")
            return response, {"type": "text"}

        # Try to use AI
        llm = self._get_llm()
        if llm:
            try:
                # Get user context data for AI
                context = await self._build_user_context(user_id)
                ai_response = await llm.chat(
                    user_message=text,
                    context=context,
                )
                # Check if the LLM returned an error message
                if ai_response and "tuve un problema al procesar" in ai_response:
                    logger.warning("LLM returned error, falling back to local response")
                    raise Exception("LLM API error")
                await self._save_message(user_id, "bot", ai_response, "text")
                return ai_response, {"type": "ai_response"}
            except Exception as e:
                logger.error(f"LLM chat failed: {e}", exc_info=True)
                # Fall through to local fallback

        # Fallback if no AI key configured or AI failed
        response = (
            "Hola, actualmente no tengo conexión con mi servicio de IA. 🧠\n\n"
            "Pero aún puedo ayudarte:\n"
            "📸 Envíame fotos de tickets para procesarlos con OCR\n"
            "📊 Consulta tu Dashboard para ver tus finanzas\n"
            "🛒 Revisa tu lista de compras inteligente\n\n"
            "Si necesitas asistencia personalizada, contacta a soporte."
        )
        await self._save_message(user_id, "bot", response, "text")
        return response, {"type": "fallback"}

    async def _build_user_context(self, user_id: str) -> str:
        """Build context string with user's real data for the AI."""
        parts = []

        # Get recent tickets
        try:
            tickets_result = await self.db.execute(
                select(Ticket)
                .where(Ticket.user_id == user_id)
                .order_by(desc(Ticket.created_at))
                .limit(10)
            )
            tickets = tickets_result.scalars().all()
            if tickets:
                parts.append("## TICKETS RECIENTES:")
                for t in tickets:
                    warranty = "🔧" if t.has_warranty_items else ""
                    parts.append(
                        f"- {warranty} {t.store_name}: ${t.total_amount:.2f} "
                        f"({t.purchase_date})"
                    )
        except Exception as e:
            logger.error(f"Error loading tickets for context: {e}")

        # Get shopping lists
        try:
            lists_result = await self.db.execute(
                select(ShoppingList)
                .where(ShoppingList.user_id == user_id)
                .order_by(desc(ShoppingList.created_at))
                .limit(5)
            )
            lists = lists_result.scalars().all()
            if lists:
                parts.append("\n## LISTAS DE COMPRAS:")
                for sl in lists:
                    parts.append(f"- {sl.title}: ${sl.estimated_total or 0:.2f} ({sl.status})")
        except Exception as e:
            logger.error(f"Error loading shopping lists: {e}")

        # Get user info
        try:
            user_result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                parts.append(f"\n## CONFIGURACIÓN:")
                parts.append(f"- Moneda: {user.currency}")
                parts.append(f"- Zona horaria: {user.timezone}")
                parts.append(f"- Telegram: {'✅ Vinculado' if user.telegram_chat_id else '❌ No vinculado'}")
                parts.append(f"- Google Drive: {'✅ Configurado' if user.encrypted_google_refresh_token else '❌ No configurado'}")
        except Exception as e:
            logger.error(f"Error loading user info: {e}")

        if not parts:
            return "El usuario no tiene datos registrados aún."

        return "\n".join(parts)

    async def _save_message(self, user_id: str, role: str, content: str, msg_type: str):
        message = ChatMessage(
            user_id=user_id,
            role=role,
            content=content,
            msg_type=msg_type,
        )
        self.db.add(message)
        await self.db.commit()

    async def get_history(self, user_id: str, limit: int = 50) -> List[dict]:
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(limit)
        )
        messages = result.scalars().all()
        return [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "msg_type": m.msg_type,
                "created_at": m.created_at.isoformat(),
            }
            for m in reversed(messages)
        ]