"""
Sistema Financiero - Telegram Bot Entry Point
Standalone process that runs the Telegram bot in polling mode.
Run with: python -m bot_main  (or  python bot_main.py)
"""
import logging
import sys
import os

# Ensure the app package is importable when running from the backend/ directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.modules.bots.telegram_bot import TelegramBot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("🚀 Iniciando Telegram Bot (standalone)...")
    bot = TelegramBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("⛔ Bot detenido por el usuario.")
    except Exception as e:
        logger.exception(f"❌ Error fatal en el bot: {e}")
        raise


if __name__ == "__main__":
    main()