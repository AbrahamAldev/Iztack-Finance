"""
Iztack-Finance - Scheduler (APScheduler)
Runs periodic tasks: daily analysis, weekly shopping list, warranty alerts.
Integrated into FastAPI lifespan — no separate worker needed.
"""
import logging
from datetime import date, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import func, desc
from app.database.connection import SyncSession
from app.database.models import Ticket, Product, User

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def run_daily_analysis():
    """Run at 23:00 daily — analyze today's spending and alert on leaks."""
    logger.info("Scheduler: daily analysis starting...")
    db = SyncSession()
    try:
        today = date.today()
        yesterday = today - timedelta(days=1)
        users = db.query(User).filter(User.is_active == True).all()

        for user in users:
            tickets = db.query(Ticket).filter(
                Ticket.user_id == user.id,
                Ticket.purchase_date == yesterday,
            ).all()
            if not tickets:
                continue

            total = sum(t.total_amount or 0 for t in tickets)
            stores = len(set(t.store_name for t in tickets))

            # Notify via Telegram if linked
            if user.telegram_chat_id:
                try:
                    # Use raw telegram API to send notification
                    import os
                    import requests
                    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
                    if bot_token:
                        msg = (
                            f"📊 *Resumen del día {yesterday.strftime('%d/%m')}*\n\n"
                            f"🛒 {len(tickets)} ticket(s) en {stores} tienda(s)\n"
                            f"💰 Total gastado: *${total:,.2f}*\n\n"
                            "📈 Revisa tu dashboard para más detalle."
                        )
                        requests.post(
                            f"https://api.telegram.org/bot{bot_token}/sendMessage",
                            json={"chat_id": user.telegram_chat_id, "text": msg, "parse_mode": "Markdown"},
                            timeout=10,
                        )
                        logger.info(f"Daily analysis sent to {user.email}")
                except Exception as e:
                    logger.error(f"Failed to notify {user.email}: {e}")
    except Exception as e:
        logger.error(f"Daily analysis error: {e}", exc_info=True)
    finally:
        db.close()


async def run_weekly_shopping_list():
    """Run Sunday 08:00 — generate shopping list based on consumption patterns."""
    logger.info("Scheduler: weekly shopping list generation...")
    db = SyncSession()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        for user in users:
            # Check for products bought 2+ times in last 30 days
            thirty_days_ago = date.today() - timedelta(days=30)
            products = (
                db.query(Product.name, func.count(Product.id).label("count"))
                .join(Ticket)
                .filter(
                    Ticket.user_id == user.id,
                    Ticket.purchase_date >= thirty_days_ago,
                    Product.is_consumable == True,
                )
                .group_by(Product.name)
                .having(func.count(Product.id) >= 2)
                .order_by(desc("count"))
                .limit(10)
                .all()
            )
            if not products:
                continue

            items = "\n".join(f"• {p.name} ({p.count}x este mes)" for p in products)

            if user.telegram_chat_id:
                try:
                    import os
                    import requests
                    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
                    if bot_token:
                        requests.post(
                            f"https://api.telegram.org/bot{bot_token}/sendMessage",
                            json={
                                "chat_id": user.telegram_chat_id,
                                "text": f"🛒 *Lista de compras sugerida*\n\n{items}\n\nRevisa el dashboard para ajustar.",
                                "parse_mode": "Markdown",
                            },
                            timeout=10,
                        )
                except Exception as e:
                    logger.error(f"Failed to send list to {user.email}: {e}")
    except Exception as e:
        logger.error(f"Weekly list error: {e}", exc_info=True)
    finally:
        db.close()


async def run_warranty_alerts():
    """Run daily at 09:00 — alert on warranties expiring in ≤30 days."""
    logger.info("Scheduler: warranty alerts checking...")
    db = SyncSession()
    try:
        today = date.today()
        thirty_days = today + timedelta(days=30)
        expiring = (
            db.query(Product)
            .join(Ticket)
            .filter(
                Product.has_warranty == True,
                Product.warranty_end_date.isnot(None),
                Product.warranty_end_date <= thirty_days,
                Product.warranty_end_date >= today,
            )
            .all()
        )
        for p in expiring:
            user = db.query(User).filter(User.id == p.ticket.user_id).first()
            if user and user.telegram_chat_id:
                days_left = (p.warranty_end_date - today).days
                try:
                    import os
                    import requests
                    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
                    if bot_token:
                        requests.post(
                            f"https://api.telegram.org/bot{bot_token}/sendMessage",
                            json={
                                "chat_id": user.telegram_chat_id,
                                "text": (
                                    f"⚠️ *Garantía por vencer*\n\n"
                                    f"🔧 *{p.name}*\n"
                                    f"📅 Vence en *{days_left} días* ({p.warranty_end_date.strftime('%d/%m/%Y')})\n"
                                    f"🏪 {p.ticket.store_name}\n\n"
                                    "Revisa el producto antes de que expire la garantía."
                                ),
                                "parse_mode": "Markdown",
                            },
                            timeout=10,
                        )
                except Exception as e:
                    logger.error(f"Warranty alert failed: {e}")
    except Exception as e:
        logger.error(f"Warranty alert error: {e}", exc_info=True)
    finally:
        db.close()


def start_scheduler():
    """Start all scheduled tasks."""
    # Daily analysis at 23:00
    scheduler.add_job(run_daily_analysis, CronTrigger(hour=23, minute=0), id="daily_analysis")
    # Weekly shopping list: Sunday at 08:00
    scheduler.add_job(run_weekly_shopping_list, CronTrigger(day_of_week="sun", hour=8, minute=0), id="weekly_list")
    # Warranty alerts at 09:00
    scheduler.add_job(run_warranty_alerts, CronTrigger(hour=9, minute=0), id="warranty_alerts")
    scheduler.start()
    logger.info("✅ Scheduler started: daily(23:00), weekly(Sun 08:00), warranties(09:00)")


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("Scheduler shut down")