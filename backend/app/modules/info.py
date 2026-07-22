"""Iztack-Finance - System Info & Pipeline Diagnostics."""
from fastapi import APIRouter, Request
from datetime import datetime
import os

router = APIRouter(tags=["System"])


@router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/pipeline")
async def pipeline_health():
    """Check the health of the entire processing pipeline."""
    import requests

    results = {"timestamp": datetime.utcnow().isoformat()}

    # 1. Backend
    results["backend"] = "up"

    # 2. DB
    try:
        from app.database.connection import SyncSession
        from sqlalchemy import text
        db = SyncSession()
        db.execute(text("SELECT 1"))
        db.close()
        results["database"] = "connected"
    except Exception as e:
        results["database"] = f"error: {str(e)[:100]}"

    # 3. OpenRouter
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if api_key and api_key.startswith("sk-or-v1-"):
        results["openrouter"] = "configured"
    else:
        results["openrouter"] = "not_configured"

    # 4. Telegram
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if bot_token:
        try:
            r = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=5)
            if r.status_code == 200:
                results["telegram"] = f"connected ({r.json().get('result', {}).get('username', 'unknown')})"
            else:
                results["telegram"] = f"error: {r.status_code}"
        except Exception as e:
            results["telegram"] = f"error: {str(e)[:50]}"
    else:
        results["telegram"] = "not_configured"

    # 5. Tickets in DB
    try:
        from app.database.connection import SyncSession
        from app.database.models import Ticket, ProcessingError, PipelineTrace
        db = SyncSession()
        ticket_count = db.query(Ticket).count()
        error_count = db.query(ProcessingError).count()
        recent_tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).limit(3).all()
        # Pipeline traces
        traces = db.query(PipelineTrace).order_by(PipelineTrace.created_at.desc()).limit(10).all()
        db.close()

        results["tickets"] = {
            "count": ticket_count,
            "errors_logged": error_count,
            "recent": [
                {"store": t.store_name, "date": str(t.purchase_date), "total": t.total_amount, "status": t.status}
                for t in recent_tickets
            ],
        }
        results["pipeline_traces"] = [
            {"step": t.step, "status": t.status, "duration_ms": t.duration_ms, "created_at": t.created_at.isoformat()}
            for t in traces
        ]
    except Exception as e:
        results["tickets"] = f"error: {str(e)[:100]}"

    # 6. Scheduler
    try:
        from app.scheduler import scheduler
        jobs = scheduler.get_jobs()
        results["scheduler"] = {"running": scheduler.running, "jobs": [j.id for j in jobs]}
    except Exception as e:
        results["scheduler"] = f"error: {str(e)[:50]}"

    # 7. Disk & RAM
    try:
        import shutil
        disk = shutil.disk_usage("/")
        results["disk"] = {
            "total_gb": round(disk.total / 1e9, 1),
            "used_gb": round(disk.used / 1e9, 1),
            "free_gb": round(disk.free / 1e9, 1),
            "percent": round(disk.used / disk.total * 100, 1)
        }
    except Exception as e:
        results["disk"] = f"error: {str(e)[:50]}"

    # Overall status
    has_errors = any(isinstance(v, str) and v.startswith("error:") for v in results.values() if isinstance(v, str))
    results["status"] = "degraded" if has_errors else "healthy"
    return results