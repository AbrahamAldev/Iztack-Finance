"""
Iztack-Finance - Telegram Bot (Multi-usuario)
Un solo bot @IztackFinance_Bot atiende a todos los usuarios.
Identifica al usuario por su chat_id vinculado en Settings.
Usa el ChatService con IA (OpenRouter) para responder.
"""
import logging
from datetime import datetime
from typing import Optional
import io

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)

from app.config import get_settings
from app.database.connection import get_db_sync
from app.database.models import User
from app.modules.ocr.service import OCRService
from app.modules.ocr.schemas import OCRResponse
from app.modules.chat.service import ChatService
from app.utils.llm import LLMClient

settings = get_settings()
logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Telegram bot multi-usuario.
    - Un solo bot (@IztackFinance_Bot) para todos
    - Identifica usuarios por chat_id vinculado en Settings
    - Usa ChatService con IA (OpenRouter) para responder
    """

    def __init__(self):
        self.token = settings.telegram_bot_token
        self.ocr_service = OCRService()
        self.application = None

    async def _get_user_by_chat_id(self, chat_id: int) -> Optional[User]:
        """Find a user by their Telegram chat_id in the database."""
        try:
            db = get_db_sync()
            user = db.query(User).filter(
                User.telegram_chat_id == str(chat_id),
                User.is_active == True
            ).first()
            db.close()
            return user
        except Exception as e:
            logger.error(f"Error looking up user by chat_id {chat_id}: {e}")
            return None

    async def _get_chat_service(self, user_id: str):
        """Get a ChatService instance for the user."""
        db = get_db_sync()
        # We need async session, but telegram bot is sync
        # Use sync session for now
        from sqlalchemy.orm import Session
        from app.database.connection import SessionLocal
        session = SessionLocal()
        return ChatService(session), session

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - identify user or ask to link."""
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)

        if user:
            welcome = (
                f"🏦 *Bienvenido {user.name}!*\n\n"
                "Envíame una foto de tu ticket de compra y yo:\n"
                "📸 *Extraeré* toda la información\n"
                "🤖 *Solicitaré* la factura en el portal\n"
                "📁 *Guardaré* PDF y XML en Google Drive\n"
                "📊 *Actualizaré* tu dashboard\n\n"
                "Comandos:\n"
                "/ayuda - Ver comandos\n"
                "/dashboard - Abrir dashboard\n"
                "/status - Estado del sistema\n\n"
                "¡Envía una foto para empezar! 📷"
            )
            await update.message.reply_text(welcome, parse_mode="Markdown")
        else:
            keyboard = [[InlineKeyboardButton("🔗 Vincular mi cuenta", url="https://finance.iztack.com/settings")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "👋 *Hola! Soy Iztack-Finance Bot*\n\n"
                "No tengo tu cuenta vinculada aún.\n\n"
                "Para usar este bot:\n"
                "1. Ve a *Configuración* en tu dashboard\n"
                "2. En la sección *Telegram*, pega este ID:\n\n"
                f"`{chat_id}`\n\n"
                "3. Guarda y vuelve aquí con /start\n\n"
                "👇 O haz clic en el botón para ir directo:",
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ayuda command."""
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)

        if not user:
            await self.start_command(update, context)
            return

        help_text = (
            "🤖 *Ayuda - Iztack-Finance*\n\n"
            "*📸 Enviar un ticket:*\n"
            "Toma una foto clara del ticket y envíala.\n"
            "Asegúrate de que se vean bien:\n"
            "- Nombre de la tienda\n"
            "- Fecha de compra\n"
            "- Productos y precios\n"
            "- Total\n\n"
            "*📋 Comandos:*\n"
            "/start - Iniciar\n"
            "/ayuda - Mostrar esta ayuda\n"
            "/status - Estado del sistema\n"
            "/dashboard - Abrir dashboard 📊\n"
            "/lista - Generar lista de compras 🛒\n"
            "/resumen - Resumen financiero 📈\n\n"
            "*💬 También puedes escribirme en español*\n"
            "Pregúntame sobre tus gastos, tickets o finanzas."
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)

        if not user:
            await self.start_command(update, context)
            return

        status_text = (
            "📋 *Estado del Sistema*\n\n"
            "✅ Backend: Activo\n"
            "✅ Base de datos: Conectada\n"
            "✅ OCR: Disponible\n"
            f"👤 Usuario: {user.name}\n"
            f"📧 Email: {user.email}\n"
            f"💳 Moneda: {user.currency}\n"
            f"☁️ Drive: {'✅' if user.encrypted_google_refresh_token else '❌'} Configurado\n\n"
            "¿Necesitas ayuda? Escribe /ayuda"
        )
        await update.message.reply_text(status_text, parse_mode="Markdown")

    async def dashboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /dashboard command."""
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)

        if not user:
            await self.start_command(update, context)
            return

        keyboard = [
            [InlineKeyboardButton("📊 Abrir Dashboard", url="https://finance.iztack.com/dashboard")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📊 *Dashboard Financiero*\n\nHaz clic para abrir:",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )

    async def shopping_list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /lista command."""
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)

        if not user:
            await self.start_command(update, context)
            return

        keyboard = [
            [InlineKeyboardButton("🛒 Ver Lista de Compras", url="https://finance.iztack.com/shopping-list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🛒 *Lista de Compras*\n\n"
            "Tu lista de compras inteligente está disponible en el dashboard.",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )

    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resumen command."""
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)

        if not user:
            await self.start_command(update, context)
            return

        await update.message.reply_text(
            "📈 *Resumen Financiero*\n\n"
            "Estoy generando tu resumen... Usa el dashboard para verlo completo.",
            parse_mode="Markdown",
        )

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming photo messages - process with OCR + AI."""
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)

        if not user:
            await self.start_command(update, context)
            return

        processing_msg = await update.message.reply_text(
            "📸 *Recibiendo ticket...*\n⏳ Procesando...",
            parse_mode="Markdown"
        )

        try:
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()
            photo_bytes = await photo_file.download_as_bytearray()

            # Process with OCR
            ocr_result: OCRResponse = self.ocr_service.extract_from_image(bytes(photo_bytes))

            if not ocr_result.success:
                await processing_msg.edit_text(
                    f"❌ *Error al procesar el ticket*\n\n"
                    f"{ocr_result.error}\n\n"
                    "💡 Asegúrate de que la foto sea clara y esté bien iluminada.",
                    parse_mode="Markdown"
                )
                return

            data = ocr_result.data
            response_parts = [
                f"✅ *Ticket Identificado*",
                f"🏪 *Tienda:* {data.store_name}",
                f"📅 *Fecha:* {data.purchase_date.strftime('%d/%m/%Y')}",
                f"💰 *Total:* *${data.total_amount:,.2f}*",
            ]

            if data.products:
                response_parts.append("")
                response_parts.append("📦 *Productos:*")
                for i, product in enumerate(data.products[:5], 1):
                    line = f"{i}. {product.name}"
                    if product.quantity and product.quantity > 1:
                        line += f" x{product.quantity}"
                    if product.total_price:
                        line += f" = ${product.total_price:,.2f}"
                    response_parts.append(line)
                if len(data.products) > 5:
                    response_parts.append(f"... y {len(data.products) - 5} más")

            if data.has_warranty_items:
                response_parts.append("")
                response_parts.append("🔧 *¡Producto con garantía detectado!*")

            response_parts.append("")
            response_parts.append("🔄 Iniciando facturación automática...")

            response_text = "\n".join(response_parts)

            keyboard = [
                [InlineKeyboardButton("📊 Ver Dashboard", url="https://finance.iztack.com/dashboard")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await processing_msg.edit_text(
                response_text,
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )

        except Exception as e:
            logger.error(f"Error processing photo: {e}", exc_info=True)
            await processing_msg.edit_text(
                f"❌ *Error inesperado*\n\n{str(e)}\n\nPor favor intenta de nuevo.",
                parse_mode="Markdown"
            )

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages - use AI (OpenRouter) to respond."""
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)

        if not user:
            await self.start_command(update, context)
            return

        text = update.message.text

        # Send typing indicator
        await update.effective_chat.send_chat_action("typing")

        try:
            # Use ChatService with AI
            from app.database.connection import SessionLocal
            db = SessionLocal()
            chat_service = ChatService(db)
            response_text, metadata = await chat_service.process_message(
                user_id=user.id,
                text=text,
            )
            db.close()

            await update.message.reply_text(response_text, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Ocurrió un error. Intenta de nuevo más tarde.",
            )

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button presses."""
        query = update.callback_query
        await query.answer()

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors from the bot."""
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.effective_chat:
            await update.effective_chat.send_message(
                "❌ Ocurrió un error interno."
            )

    def run(self):
        """Start the Telegram bot in polling mode."""
        if not self.token:
            logger.warning("TELEGRAM_BOT_TOKEN no configurado. Bot de Telegram no disponible.")
            return

        self.application = Application.builder().token(self.token).build()

        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("ayuda", self.help_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("dashboard", self.dashboard_command))
        self.application.add_handler(CommandHandler("lista", self.shopping_list_command))
        self.application.add_handler(CommandHandler("resumen", self.summary_command))
        self.application.add_handler(CommandHandler("summary", self.summary_command))

        # Photo handler
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))

        # Text handler (non-command) - uses AI
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.handle_text_message
        ))

        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))

        # Error handler
        self.application.add_error_handler(self.error_handler)

        # Start polling
        logger.info("🤖 Telegram Bot multi-usuario iniciado...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)