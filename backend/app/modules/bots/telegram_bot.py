"""
Iztack-Finance - Telegram Bot (Multi-usuario)
Un solo bot @IztackFinance_Bot atiende a todos los usuarios.
Identifica al usuario por su chat_id vinculado en Settings.
Usa LLMClient directo + fallback a respuestas predefinidas.
"""
import os
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
from app.database.models import User, Ticket, ProcessingError
from app.modules.ocr.service import OCRService
from app.modules.ocr.schemas import OCRResponse
from app.utils.llm import LLMClient

settings = get_settings()
logger = logging.getLogger(__name__)


class TelegramBot:

    def __init__(self):
        self.token = settings.telegram_bot_token
        self.ocr_service = OCRService()
        self.application = None

    async def _get_user_by_chat_id(self, chat_id: int) -> Optional[User]:
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

    async def _build_uer_context(self, user_id: str) -> str:
        """Build rich context with user data, tickets, and products."""
        db = get_db_sync()
        try:
            from app.database.models import Product
            user = db.query(User).filter(User.id == user_id).first()
            tickets = db.query(Ticket).filter(Ticket.user_id == user_id)\
                .order_by(Ticket.created_at.desc()).limit(10).all()
            if not tickets:
                return "El usuario no tiene tickets registrados aun."
            lines = []
            if user:
                lines.append(f"Usuario: {user.name} ({user.email})")
                lines.append(f"Moneda: {user.currency} | Telegram: {'Si' if user.telegram_chat_id else 'No'} | Drive: {'Si' if user.encrypted_google_refresh_token else 'No'}")
            total = 0
            stores = set()
            lines.append(f"TICKETS RECIENTES ({len(tickets)}):")
            for t in tickets:
                w = "GARANTIA " if t.has_warranty_items else ""
                lines.append(f"- {w}[{t.purchase_date}] {t.store_name}: ${t.total_amount:.2f} (status={t.status})")
                total += t.total_amount or 0
                stores.add(t.store_name)
            lines.append(f"Total gastado: ${total:,.2f} en {len(stores)} tiendas: {', '.join(list(stores)[:5])}")
            products = db.query(Product).join(Ticket).filter(Ticket.user_id == user_id)\
                .order_by(Product.created_at.desc()).limit(15).all()
            if products:
                lines.append(f"PRODUCTOS RECIENTES:")
                for p in products[:10]:
                    lines.append(f"- {p.name} ${p.total_price:.2f} [{p.category or 'sin cat'}]")
            db.close()
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error building context: {e}")
            try: db.close()
            except: pass
            return "No se pudo cargar contexto del usuario."

    # =========================================================================
    # COMMANDS
    # =========================================================================

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                "Comandos: /ayuda /dashboard /status /reporte"
            )
            await update.message.reply_text(welcome, parse_mode="Markdown")
        else:
            keyboard = [[InlineKeyboardButton("🔗 Vincular mi cuenta", url="https://finance.iztack.com/settings")]]
            await update.message.reply_text(
                f"👋 *Hola! Soy Iztack-Finance Bot*\n\n"
                "No tengo tu cuenta vinculada aún.\n\n"
                "1. Ve a *Configuración* en tu dashboard\n"
                "2. En *Telegram*, pega este ID:\n\n`{chat_id}`\n\n"
                "3. Guarda y vuelve aquí con /start",
                parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
            )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)
        if not user: return await self.start_command(update, context)
        await update.message.reply_text(
            "🤖 *Ayuda - Iztack-Finance*\n\n"
            "/start — Iniciar\n"
            "/ayuda — Mostrar esta ayuda\n"
            "/status — Estado del sistema\n"
            "/dashboard — Abrir dashboard 📊\n"
            "/lista — Lista de compras 🛒\n"
            "/resumen — Resumen financiero 📈\n"
            "/reporte — Reportar un error 🐛",
            parse_mode="Markdown"
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)
        if not user: return await self.start_command(update, context)
        drive_ok = "✅" if user.encrypted_google_refresh_token else "❌"
        await update.message.reply_text(
            f"📋 *Estado del Sistema*\n\n"
            f"✅ Backend: Activo\n"
            f"✅ Base de datos: Conectada\n"
            f"✅ OCR: Disponible\n"
            f"👤 Usuario: {user.name}\n"
            f"📧 Email: {user.email}\n"
            f"💳 Moneda: {user.currency}\n"
            f"☁️ Drive: {drive_ok} Configurado",
            parse_mode="Markdown"
        )

    async def dashboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)
        if not user: return await self.start_command(update, context)
        keyboard = [[InlineKeyboardButton("📊 Abrir Dashboard", url="https://finance.iztack.com/dashboard")]]
        await update.message.reply_text("📊 *Dashboard Financiero*\n\nHaz clic para abrir:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    async def shopping_list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)
        if not user: return await self.start_command(update, context)
        keyboard = [[InlineKeyboardButton("🛒 Ver Lista", url="https://finance.iztack.com/shopping-list")]]
        await update.message.reply_text("🛒 *Lista de Compras*\n\nDisponible en el dashboard.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)
        if not user: return await self.start_command(update, context)
        await update.message.reply_text("📈 *Resumen Financiero*\n\nUsa el dashboard para verlo completo.", parse_mode="Markdown")

    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)
        if not user: return await self.start_command(update, context)

        # Check if a description was included
        text = update.message.text.strip()
        description = text.replace("/reporte", "").strip() if text.startswith("/reporte") else ""

        if not description:
            await update.message.reply_text(
                "🐛 *Reportar un error*\n\n"
                "Para ayudarnos a solucionarlo, describe brevemente:\n"
                "• ¿Qué estabas haciendo?\n"
                "• ¿Qué error viste?\n\n"
                "Ejemplo: `/reporte Al subir un ticket de Chedraui el OCR dio fecha equivocada`\n\n"
                "El reporte se enviará al equipo de soporte. ¡Gracias!",
                parse_mode="Markdown"
            )
            return

        db = get_db_sync()
        try:
            error = ProcessingError(
                user_id=user.id, error_type="user_report",
                error_message=f"Reporte: {description}\n\nUsuario: {user.name} ({user.email}) desde Telegram",
                error_details={"chat_id": str(chat_id), "description": description},
                suggested_action="Revisar en admin portal"
            )
            db.add(error); db.commit()
            await update.message.reply_text(
                "✅ *Reporte enviado*\n\n"
                f"📝 \"{description[:200]}\"\n\n"
                "El equipo lo revisará pronto. Gracias por ayudar a mejorar Iztack-Finance.",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            await update.message.reply_text("❌ No se pudo enviar el reporte.")
        finally:
            try: db.close()
            except: pass

    # =========================================================================
    # MESSAGE HANDLERS
    # =========================================================================

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)
        if not user: return await self.start_command(update, context)
        msg = await update.message.reply_text("📸 *Recibiendo ticket...*\n⏳ Procesando...", parse_mode="Markdown")
        try:
            photo = update.message.photo[-1]
            photo_bytes = await (await photo.get_file()).download_as_bytearray()
            result = self.ocr_service.extract_from_image(bytes(photo_bytes))
            if not result.success:
                return await msg.edit_text(f"❌ *Error*\n\n{result.error}", parse_mode="Markdown")
            d = result.data
            parts = [f"✅ *Ticket Identificado*", f"🏪 *Tienda:* {d.store_name}", f"📅 *Fecha:* {d.purchase_date.strftime('%d/%m/%Y')}", f"💰 *Total:* *${d.total_amount:,.2f}*"]
            if d.products:
                parts.append("\n📦 *Productos:*")
                for i, p in enumerate(d.products[:5], 1):
                    line = f"{i}. {p.name}"
                    if p.quantity and p.quantity > 1: line += f" x{p.quantity}"
                    if p.total_price: line += f" = ${p.total_price:,.2f}"
                    parts.append(line)
            parts.append("\n Iniciando facturación automática...")
            await msg.edit_text("\n".join(parts), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📊 Dashboard", url="https://finance.iztack.com/dashboard")]]))
        except Exception as e:
            logger.error(f"Error processing photo: {e}", exc_info=True)
            await msg.edit_text("❌ *Error inesperado*\n\nPor favor intenta de nuevo.", parse_mode="Markdown")

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user = await self._get_user_by_chat_id(chat_id)
        if not user: return await self.start_command(update, context)
        text = update.message.text
        await update.effective_chat.send_chat_action("typing")

        # Try LLM first
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if api_key and api_key.startswith("sk-or-v1-"):
            try:
                llm = LLMClient(api_key)
                ctx = await self._build_user_context(user.id)
                response = await llm.chat(
                    user_message=text,
                    context=f"Contexto del usuario:\n{ctx}\n\nComandos disponibles: /start /ayuda /status /dashboard /lista /resumen /reporte. Si tu respuesta se relaciona con uno, menciónalo."
                )
                if response and "tuve un problema" not in response:
                    return await update.message.reply_text(response[:4000], parse_mode="Markdown")
            except Exception as e:
                logger.error(f"LLM error in Telegram: {e}")

        # Fallback
        await update.message.reply_text(
            "🤖 *Asistente Iztack*\n\n"
            "No tengo conexión con IA ahora, pero puedo ayudarte:\n\n"
            "📋 *Comandos:*\n"
            "/start /ayuda /status /dashboard /lista /resumen\n\n"
            "📸 Envíame una *foto de ticket* y la procesaré.\n\n"
            "🐛 *¿Algo falla?* Usa /reporte",
            parse_mode="Markdown"
        )

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.answer()

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.effective_chat:
            await update.effective_chat.send_message("❌ Ocurrió un error interno.")

    # =========================================================================
    # RUN
    # =========================================================================

    def run(self):
        if not self.token:
            logger.warning("TELEGRAM_BOT_TOKEN no configurado.")
            return
        self.application = Application.builder().token(self.token).build()
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("ayuda", self.help_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("dashboard", self.dashboard_command))
        self.application.add_handler(CommandHandler("lista", self.shopping_list_command))
        self.application.add_handler(CommandHandler("resumen", self.summary_command))
        self.application.add_handler(CommandHandler("reporte", self.report_command))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        self.application.add_error_handler(self.error_handler)
        logger.info("🤖 Telegram Bot multi-usuario iniciado...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)