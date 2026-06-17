"""
Sistema Financiero - Telegram Bot
Handles incoming messages, photo processing, and user interactions via Telegram.
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
from app.modules.ocr.service import OCRService
from app.modules.ocr.schemas import OCRResponse

settings = get_settings()
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for receiving ticket photos and sending responses."""

    def __init__(self):
        self.token = settings.telegram_bot_token
        self.authorized_chat_ids = self._parse_authorized_chats()
        self.ocr_service = OCRService()
        self.application = None

    def _parse_authorized_chats(self) -> list:
        """Parse authorized chat IDs from settings."""
        chats = settings.telegram_chat_id_authorized
        if not chats:
            return []
        return [c.strip() for c in chats.split(",") if c.strip()]

    def _is_authorized(self, chat_id: int) -> bool:
        """Check if a chat is authorized to use the bot."""
        if not self.authorized_chat_ids:
            return True  # Allow all if not configured
        return str(chat_id) in self.authorized_chat_ids

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        chat_id = update.effective_chat.id
        
        if not self._is_authorized(chat_id):
            await update.message.reply_text(
                "❌ No estás autorizado para usar este bot.\n"
                "Contacta al administrador para obtener acceso."
            )
            return
        
        welcome_text = (
            "🏦 *Bienvenido al Sistema Financiero*\n\n"
            "Envíame una foto de tu ticket de compra y yo:\n"
            "📸 *Extraeré* toda la información del ticket\n"
            "🤖 *Solicitaré* la factura en el portal de la tienda\n"
            "📁 *Guardaré* PDF y XML en Google Drive\n"
            "📊 *Actualizaré* tu dashboard financiero\n\n"
            "Comandos disponibles:\n"
            "/start - Iniciar\n"
            "/status - Estado del último ticket\n"
            "/facturas - Resumen de facturación\n"
            "/dashboard - Link al dashboard\n"
            "/lista - Generar lista de compras\n"
            "/resumen - Resumen financiero del mes\n"
            "/ayuda - Ayuda\n\n"
            "¡Envía una foto para empezar! 📷"
        )
        
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ayuda command."""
        help_text = (
            "🤖 *Ayuda - Sistema Financiero*\n\n"
            "*📸 Enviar un ticket:*\n"
            "Toma una foto clara del ticket y envíala.\n"
            "Asegúrate de que se vean bien:\n"
            "- Nombre de la tienda\n"
            "- Fecha de compra\n"
            "- Productos y precios\n"
            "- Total\n\n"
            "*📋 Comandos:*\n"
            "/start - Iniciar conversación\n"
            "/status - Ver estado del último ticket\n"
            "/facturas - Resumen de facturación del mes\n"
            "/dashboard - Abrir dashboard web 📊\n"
            "/lista - Generar lista de compras 🛒\n"
            "/resumen - Resumen financiero 📈\n"
            "/ayuda - Mostrar esta ayuda\n\n"
            "*❓ Preguntas frecuentes:*\n"
            "¿No se ve bien el ticket? Asegúrate de buena iluminación\n"
            "¿Ticket vencido? Solo process tickets < 60 días\n"
            "¿Error? El bot te notificará y sugerirá soluciones"
        )
        
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        # TODO: Query last ticket from database
        await update.message.reply_text(
            "📋 *Estado*\n\n"
            "Función en desarrollo. Pronto podrás ver el estado de tus tickets aquí.",
            parse_mode="Markdown"
        )

    async def dashboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /dashboard command."""
        # TODO: Generate dashboard link with auth
        dashboard_url = "http://localhost:3000/dashboard"
        
        keyboard = [
            [InlineKeyboardButton("📊 Abrir Dashboard", url=dashboard_url)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📊 *Dashboard Financiero*\n\n"
            "Haz clic en el botón para abrir el dashboard:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    async def shopping_list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /lista command."""
        # TODO: Generate shopping list
        await update.message.reply_text(
            "🛒 *Lista de Compras*\n\n"
            "Función en desarrollo. Pronto podrás generar y compartir "
            "listas de compras inteligentes aquí.",
            parse_mode="Markdown"
        )

    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resumen command."""
        # TODO: Generate financial summary
        await update.message.reply_text(
            "📈 *Resumen Financiero*\n\n"
            "Función en desarrollo. Pronto tendrás tu resumen mensual aquí.",
            parse_mode="Markdown"
        )

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle incoming photo messages.
        Downloads the photo, runs OCR, and responds with extracted data.
        """
        chat_id = update.effective_chat.id
        
        if not self._is_authorized(chat_id):
            await update.message.reply_text("❌ No autorizado.")
            return
        
        # Send initial processing message
        processing_msg = await update.message.reply_text(
            "📸 *Recibiendo ticket...*\n"
            "⏳ Procesando OCR...",
            parse_mode="Markdown"
        )
        
        try:
            # Get the largest photo
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()
            
            # Download photo bytes
            photo_bytes = await photo_file.download_as_bytearray()
            
            # Process with OCR
            ocr_result: OCRResponse = self.ocr_service.extract_from_image(bytes(photo_bytes))
            
            if not ocr_result.success:
                await processing_msg.edit_text(
                    f"❌ *Error al procesar el ticket*\n\n"
                    f"{ocr_result.error}\n\n"
                    "💡 *Sugerencia:* Asegúrate de que la foto sea clara "
                    "y esté bien iluminada. Intenta de nuevo.",
                    parse_mode="Markdown"
                )
                return
            
            data = ocr_result.data
            
            # Build response message
            response_parts = [
                f"✅ *Ticket Identificado*\n",
                f"🏪 *Tienda:* {data.store_name}",
                f"📅 *Fecha:* {data.purchase_date.strftime('%d/%m/%Y')}",
                f"🕐 *Hora:* {data.purchase_time or 'N/A'}",
                f"🧾 *Folio:* {data.receipt_number or 'N/A'}",
                f"",
                f"💵 *Subtotal:* ${data.subtotal:,.2f}" if data.subtotal else "",
                f"💰 *IVA:* ${data.taxes:,.2f}" if data.taxes else "",
                f"🔢 *Total:* *${data.total_amount:,.2f}*",
                f"💳 *Pago:* {data.payment_method or 'N/A'}",
                f"",
            ]
            
            # Add products
            if data.products:
                response_parts.append("📦 *Productos:*")
                for i, product in enumerate(data.products[:10], 1):  # Max 10 products
                    product_line = (
                        f"{i}. {product.name}"
                        f" x{product.quantity}"
                        f" = ${product.total_price:,.2f}"
                    )
                    if product.discount:
                        product_line += f" (-${product.discount:,.2f})"
                    response_parts.append(product_line)
                
                if len(data.products) > 10:
                    response_parts.append(f"... y {len(data.products) - 10} productos más")
                
                response_parts.append("")
            
            # Add warranty info
            if data.has_warranty_items:
                response_parts.append(
                    "🔧 *¡Producto con garantía detectado!*\n"
                    "Se guardará en la carpeta de GARANTÍAS"
                )
                response_parts.append("")
            
            # Add status
            response_parts.append(
                "⏳ *Iniciando facturación...*\n"
                "Te notificaré cuando esté lista."
            )
            
            response_text = "\n".join(part for part in response_parts if part)
            
            # Add action buttons
            keyboard = [
                [
                    InlineKeyboardButton("📊 Ver Dashboard", url="http://localhost:3000/dashboard"),
                ],
                [
                    InlineKeyboardButton("❌ Reportar Error", callback_data="report_error"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await processing_msg.edit_text(
                response_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error processing photo: {e}", exc_info=True)
            await processing_msg.edit_text(
                f"❌ *Error inesperado*\n\n"
                f"Ocurrió un error al procesar tu ticket.\n"
                f"Error: {str(e)}\n\n"
                "Por favor intenta de nuevo más tarde.",
                parse_mode="Markdown"
            )

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (non-command)."""
        chat_id = update.effective_chat.id
        text = update.message.text
        
        if not self._is_authorized(chat_id):
            return
        
        await update.message.reply_text(
            "📸 Para procesar un ticket, envíame una *foto* del mismo.\n\n"
            "También puedes usar los comandos:\n"
            "/ayuda - Ver comandos disponibles",
            parse_mode="Markdown"
        )

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button presses."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "report_error":
            await query.edit_message_text(
                text="Por favor describe el error que encontraste.\n"
                     "El administrador lo revisará pronto."
            )

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors from the bot."""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_chat:
            await update.effective_chat.send_message(
                "❌ Ocurrió un error interno. El administrador ha sido notificado."
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
        
        # Text handler (non-command)
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.handle_text_message
        ))
        
        # Callback query handler (inline buttons)
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
        
        # Start polling
        logger.info("🤖 Telegram Bot iniciado en modo polling...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)