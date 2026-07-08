"""
Iztack-Finance - Chat Service
In-app chat with AI responses for ticket processing, queries, and commands.
"""
import logging
from datetime import datetime
from typing import List, Optional, Tuple
import json

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, ChatMessage
from app.modules.auth.service import AuthService
from app.modules.ocr.service import OCRService
from app.modules.ocr.schemas import OCRResponse
from app.modules.tickets.service import TicketsService

logger = logging.getLogger(__name__)


class ChatService:
    """Chat service that processes messages and returns AI responses."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ocr_service = OCRService()
        self.tickets_service = TicketsService()

    async def process_message(
        self, user_id: str, text: str = None, image_bytes: bytes = None
    ) -> Tuple[str, dict]:
        """
        Process a chat message (text and/or image) and return a response.
        Returns (response_text, metadata).
        """
        # Save user message
        if text:
            await self._save_message(user_id, "user", text, "text")

        # If there's an image, process it as a ticket
        if image_bytes:
            return await self._handle_ticket_image(user_id, image_bytes)

        # If only text, route to appropriate handler
        if not text:
            return "Envía una foto de tu ticket o escribe un mensaje.", {}

        return await self._handle_text_command(user_id, text.lower().strip())

    async def _handle_ticket_image(
        self, user_id: str, image_bytes: bytes
    ) -> Tuple[str, dict]:
        """Process a ticket image and return formatted result."""
        await self._save_message(user_id, "bot", "📸 Procesando imagen...", "status")

        try:
            result: OCRResponse = self.ocr_service.extract_from_image(image_bytes)

            if not result.success:
                response = (
                    "❌ *No se pudo leer el ticket*\n\n"
                    f"{result.error}\n\n"
                    "💡 *Sugerencias:*\n"
                    "• Asegúrate de buena iluminación\n"
                    "• Coloca el ticket sobre una superficie plana\n"
                    "• Evita sombras y reflejos\n"
                    "• Si el ticket es muy largo, toma 2 fotos y úsalas como continuación"
                )
                await self._save_message(user_id, "bot", response, "error")
                return response, {"type": "error", "ocr_result": result.error}

            data = result.data
            lines = [f"✅ *Ticket Identificado*", ""]

            if data.store_name:
                lines.append(f"🏪 *Tienda:* {data.store_name}")
            if data.purchase_date:
                lines.append(f"📅 *Fecha:* {data.purchase_date.strftime('%d/%m/%Y')}")
            if data.total_amount:
                lines.append(f"💰 *Total:* ${data.total_amount:,.2f}")
            if data.payment_method:
                lines.append(f"💳 *Pago:* {data.payment_method}")

            lines.append("")

            if data.products:
                lines.append("📦 *Productos:*")
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
            lines.append("🔄 *Iniciando facturación automática...*")
            lines.append("Te notificaré cuando esté lista.")

            if data.has_warranty_items:
                lines.append("")
                lines.append("🔧 *¡Producto con garantía detectado!*")
                lines.append("Se archivará en la carpeta de garantías.")

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
            logger.error(f"Chat image processing error: {e}", exc_info=True)
            error_msg = "❌ Error al procesar la imagen. Intenta de nuevo."
            await self._save_message(user_id, "bot", error_msg, "error")
            return error_msg, {"type": "error"}

    async def _handle_text_command(
        self, user_id: str, text: str
    ) -> Tuple[str, dict]:
        """Route text messages to appropriate handlers."""
        # Help
        if text in ("/ayuda", "/help", "ayuda", "help", "comandos"):
            response = (
                "🤖 *Comandos disponibles:*\n\n"
                "📸 *Envía una foto* de tu ticket para procesarlo\n"
                "📋 `/status` - Estado del último ticket\n"
                "📊 `/dashboard` - Abrir dashboard\n"
                "🛒 `/lista` - Generar lista de compras\n"
                "📈 `/resumen` - Resumen del mes\n"
                "❓ `/ayuda` - Mostrar esta ayuda"
            )
            await self._save_message(user_id, "bot", response, "command")
            return response, {"type": "command", "command": "help"}

        # Status
        if text in ("/status", "status", "estado"):
            response = (
                "📋 *Estado del sistema*\n\n"
                "✅ Backend: Activo\n"
                "✅ Base de datos: Conectada\n"
                "✅ OCR: Disponible\n"
                "⚠️ Telegram: Pendiente de configurar\n\n"
                "Pronto podrás ver el estado de tus tickets aquí."
            )
            await self._save_message(user_id, "bot", response, "status")
            return response, {"type": "status"}

        # Dashboard
        if text in ("/dashboard", "dashboard", "tablero"):
            response = "📊 Abre tu dashboard en: https://finance.iztack.com/dashboard"
            await self._save_message(user_id, "bot", response, "link")
            return response, {"type": "link"}

        # Shopping list
        if text in ("/lista", "lista", "compras"):
            response = (
                "🛒 *Lista de Compras*\n\n"
                "Función en desarrollo. Pronto podrás generar y compartir "
                "listas de compras inteligentes aquí y en la sección de Lista de Compras."
            )
            await self._save_message(user_id, "bot", response, "info")
            return response, {"type": "info"}

        # Summary
        if text in ("/resumen", "resumen", "summary"):
            response = (
                "📈 *Resumen Financiero*\n\n"
                "Aún no hay suficientes datos para generar un resumen.\n"
                "Comienza subiendo tickets para ver tus estadísticas."
            )
            await self._save_message(user_id, "bot", response, "info")
            return response, {"type": "info"}

        # Unknown command
        if text.startswith("/"):
            response = (
                f"❌ Comando *{text}* no reconocido.\n"
                "Usa `/ayuda` para ver los comandos disponibles."
            )
            await self._save_message(user_id, "bot", response, "error")
            return response, {"type": "error"}

        # General text - answer with AI
        response = self._generate_ai_response(text)
        await self._save_message(user_id, "bot", response, "text")
        return response, {"type": "text"}

    def _generate_ai_response(self, text: str) -> str:
        """Generate a simple AI response for general queries."""
        responses = {
            "hola": "¡Hola! 👋 ¿En qué puedo ayudarte?\n\nEnvía una foto de tu ticket para procesarlo o escribe `/ayuda` para ver los comandos.",
            "buenos días": "¡Buenos días! ☀️ ¿Tienes algún ticket que procesar hoy?",
            "buenas tardes": "¡Buenas tardes! 🌤️ ¿En qué puedo ayudarte?",
            "gracias": "¡De nada! 😊 Estoy aquí para ayudarte con tus finanzas.",
        }

        # Check exact matches
        for key, val in responses.items():
            if key in text:
                return val

        # Default response
        return (
            "No entendí tu mensaje. 🤔\n\n"
            "Puedes:\n"
            "📸 *Enviar una foto* de tu ticket\n"
            "📝 *Escribir un comando* como /ayuda, /status, /dashboard\n"
            "💬 *Preguntar* sobre tus finanzas"
        )

    async def _save_message(
        self, user_id: str, role: str, content: str, msg_type: str
    ):
        """Save a chat message to the database."""
        message = ChatMessage(
            user_id=user_id,
            role=role,
            content=content,
            msg_type=msg_type,
        )
        self.db.add(message)
        await self.db.commit()

    async def get_history(
        self, user_id: str, limit: int = 50
    ) -> List[dict]:
        """Get chat history for a user."""
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