"""
Sistema Financiero - Celery Configuration
Background task processing for OCR, web scraping, email search, etc.
"""
from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "sistema_financiero",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Mexico_City",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max per task
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,  # Results expire after 1 hour
)

# Auto-discover tasks from registered modules
celery_app.autodiscover_tasks([
    "app.modules.ocr",
    "app.modules.bots",
    "app.modules.facturacion",
    "app.modules.facturacion.email",
    "app.modules.almacenamiento",
    "app.modules.clasificacion",
    "app.modules.garantias",
    "app.modules.finanzas",
    "app.modules.shopping_list",
])


# =============================================================================
# Scheduled Tasks (Celery Beat)
# =============================================================================
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    # Daily financial analysis
    "generate-daily-analysis": {
        "task": "app.modules.finanzas.tasks.generate_daily_analysis",
        "schedule": crontab(hour=23, minute=0),  # Every day at 11 PM
    },
    # Weekly shopping list generation
    "generate-weekly-shopping-list": {
        "task": "app.modules.shopping_list.tasks.generate_weekly_list",
        "schedule": crontab(hour=8, minute=0, day_of_week="sunday"),  # Every Sunday 8 AM
    },
    # Monthly financial report
    "generate-monthly-report": {
        "task": "app.modules.finanzas.tasks.generate_monthly_report",
        "schedule": crontab(hour=8, minute=0, day_of_month="1"),  # 1st of each month
    },
    # Check expired tickets
    "check-expired-tickets": {
        "task": "app.modules.clasificacion.tasks.check_expired_tickets",
        "schedule": crontab(hour=6, minute=0),  # Every day at 6 AM
    },
    # Update consumption cycles
    "update-consumption-cycles": {
        "task": "app.modules.shopping_list.tasks.update_consumption_cycles",
        "schedule": crontab(hour=2, minute=0),  # Every day at 2 AM
    },
    # Check for missing purchases
    "check-missing-purchases": {
        "task": "app.modules.shopping_list.tasks.check_missing_purchases",
        "schedule": crontab(hour=20, minute=0),  # Every day at 8 PM
    },
}