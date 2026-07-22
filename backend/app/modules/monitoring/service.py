"""
Iztack-Finance - Monitoring Service
Sensors, health checks, and email alerts for the entire data pipeline.
"""
import logging
import os
import shutil
import smtplib
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional

import httpx
from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.models import (
    Ticket,
    Product,
    ProcessingError,
    PipelineTrace,
    SensorReading,
    EmailAlert,
    ConsumptionCycle,
    ShoppingList,
)

logger = logging.getLogger(__name__)


class EmailService:
    """Sends alert emails via SMTP or Gmail API fallback."""

    def __init__(self):
        self.settings = get_settings()

    def _get_recipients(self) -> List[str]:
        raw = self.settings.admin_alert_emails or ""
        return [e.strip() for e in raw.split(",") if e.strip()]

    def _send_smtp(self, subject: str, body: str, recipients: List[str]) -> bool:
        if not all([self.settings.smtp_host, self.settings.smtp_user, self.settings.smtp_password]):
            return False
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.settings.smtp_user
            msg["To"] = ", ".join(recipients)
            msg.attach(MIMEText(body, "plain", "utf-8"))
            msg.attach(MIMEText(f"<pre>{body}</pre>", "html", "utf-8"))

            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=15) as server:
                if self.settings.smtp_use_tls:
                    server.starttls()
                server.login(self.settings.smtp_user, self.settings.smtp_password)
                server.sendmail(self.settings.smtp_user, recipients, msg.as_string())
            return True
        except Exception as exc:
            logger.error(f"SMTP send failed: {exc}")
            return False

    def _send_gmail_api(self, subject: str, body: str, recipients: List[str]) -> bool:
        """Fallback using Gmail API if SMTP is not configured."""
        if not all([
            self.settings.google_refresh_token,
            self.settings.google_client_id,
            self.settings.google_client_secret,
            self.settings.gmail_sender_email,
        ]):
            return False
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            import base64

            creds = Credentials(
                token=None,
                refresh_token=self.settings.google_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.settings.google_client_id,
                client_secret=self.settings.google_client_secret,
                scopes=["https://www.googleapis.com/auth/gmail.send"],
            )
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())

            service = build("gmail", "v1", credentials=creds)
            message = MIMEMultipart("alternative")
            message["to"] = ", ".join(recipients)
            message["from"] = self.settings.gmail_sender_email
            message["subject"] = subject
            message.attach(MIMEText(body, "plain", "utf-8"))
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            service.users().messages().send(userId="me", body={"raw": raw}).execute()
            return True
        except Exception as exc:
            logger.error(f"Gmail API send failed: {exc}")
            return False

    def send_alert(self, subject: str, body: str) -> bool:
        recipients = self._get_recipients()
        if not recipients:
            logger.warning("No admin alert emails configured")
            return False

        if self._send_smtp(subject, body, recipients):
            return True
        if self._send_gmail_api(subject, body, recipients):
            return True
        logger.error("Could not send alert email via SMTP or Gmail API")
        return False


class SensorsService:
    """Collects sensor readings for the entire data pipeline and infrastructure."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self.email = EmailService()

    async def run_all_checks(self) -> Dict:
        """Run all sensor checks, save readings, and send alerts if needed."""
        start = time.time()
        readings: List[SensorReading] = []

        checks = [
            ("database", self._check_database),
            ("redis", self._check_redis),
            ("openrouter", self._check_openrouter),
            ("telegram", self._check_telegram),
            ("backend", self._check_backend),
            ("disk", self._check_disk),
            ("memory", self._check_memory),
            ("scheduler", self._check_scheduler),
            ("pipeline_tickets", self._check_pipeline_tickets),
            ("pipeline_finance", self._check_pipeline_finance),
            ("pipeline_warranty", self._check_pipeline_warranty),
            ("pipeline_shopping", self._check_pipeline_shopping),
            ("pipeline_storage", self._check_pipeline_storage),
            ("pipeline_agents", self._check_pipeline_agents),
        ]

        for component, check_fn in checks:
            try:
                result = await check_fn()
            except Exception as exc:
                result = {"status": "error", "message": f"Check exception: {exc}", "details": {}}
            reading = SensorReading(
                check_name=result.get("check_name", component),
                component=component,
                status=result.get("status", "error"),
                message=result.get("message", ""),
                details=result.get("details", {}),
            )
            readings.append(reading)

        self.db.add_all(readings)
        await self.db.commit()

        # Send alerts for new errors
        await self._notify_errors(readings)

        errors = [r for r in readings if r.status == "error"]
        warnings = [r for r in readings if r.status == "warning"]
        overall = "error" if errors else "warning" if warnings else "ok"

        return {
            "overall_status": overall,
            "checked_at": datetime.utcnow().isoformat(),
            "duration_ms": int((time.time() - start) * 1000),
            "readings_count": len(readings),
            "errors_count": len(errors),
            "warnings_count": len(warnings),
            "readings": [
                {
                    "component": r.component,
                    "check_name": r.check_name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in readings
            ],
        }

    async def _notify_errors(self, readings: List[SensorReading]):
        """Send email alerts for error readings, throttling duplicates."""
        for reading in readings:
            if reading.status not in ("error", "warning"):
                continue

            alert_key = f"{reading.component}:{reading.check_name}"
            # Check if there is an unresolved alert
            result = await self.db.execute(
                select(EmailAlert).where(
                    EmailAlert.alert_key == alert_key,
                    EmailAlert.status == reading.status,
                    EmailAlert.resolved_at.is_(None),
                ).order_by(EmailAlert.sent_at.desc()).limit(1)
            )
            last_alert = result.scalar_one_or_none()

            # Throttle: max 1 alert per hour for the same error
            if last_alert and last_alert.sent_at > datetime.utcnow() - timedelta(hours=1):
                continue

            subject = f"[Iztack-Finance] ALERTA: {reading.component} - {reading.status.upper()}"
            body = (
                f"Componente: {reading.component}\n"
                f"Check: {reading.check_name}\n"
                f"Estado: {reading.status.upper()}\n"
                f"Mensaje: {reading.message}\n"
                f"Detalles: {reading.details}\n"
                f"Hora: {datetime.utcnow().isoformat()} UTC\n\n"
                f"Panel admin: https://admfinance.iztack.com"
            )

            sent = self.email.send_alert(subject, body)
            alert = EmailAlert(
                alert_key=alert_key,
                component=reading.component,
                status=reading.status,
                message=reading.message,
                recipients=", ".join(self.email._get_recipients()),
            )
            self.db.add(alert)
            await self.db.commit()

            # Resolve older opposite alerts (e.g. previous error now ok would be handled elsewhere)

    async def _check_database(self) -> Dict:
        start = time.time()
        try:
            await self.db.execute(text("SELECT 1"))
            duration = int((time.time() - start) * 1000)
            # Count recent errors
            result = await self.db.execute(select(func.count(ProcessingError.id)))
            error_count = result.scalar()
            return {
                "check_name": "database_connection",
                "status": "ok",
                "message": "Database connection OK",
                "details": {"duration_ms": duration, "total_errors": error_count},
            }
        except Exception as exc:
            return {"check_name": "database_connection", "status": "error", "message": str(exc), "details": {}}

    async def _check_redis(self) -> Dict:
        try:
            import redis
            client = redis.from_url(self.settings.redis_url, socket_connect_timeout=3)
            client.ping()
            info = client.info()
            return {
                "check_name": "redis_connection",
                "status": "ok",
                "message": "Redis connection OK",
                "details": {"used_memory_human": info.get("used_memory_human")},
            }
        except Exception as exc:
            return {"check_name": "redis_connection", "status": "error", "message": str(exc), "details": {}}

    async def _check_openrouter(self) -> Dict:
        key = self.settings.openrouter_api_key or ""
        if not key.startswith("sk-or-v1-"):
            return {"check_name": "openrouter_key", "status": "error", "message": "OPENROUTER_API_KEY not configured", "details": {}}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    "https://openrouter.ai/api/v1/auth/key",
                    headers={"Authorization": f"Bearer {key}"},
                )
            if r.status_code == 200:
                data = r.json().get("data", {})
                return {
                    "check_name": "openrouter_api",
                    "status": "ok",
                    "message": "OpenRouter API reachable",
                    "details": {
                        "label": data.get("label"),
                        "usage": data.get("usage"),
                        "limit": data.get("limit"),
                    },
                }
            return {"check_name": "openrouter_api", "status": "warning", "message": f"HTTP {r.status_code}", "details": {}}
        except Exception as exc:
            return {"check_name": "openrouter_api", "status": "error", "message": str(exc), "details": {}}

    async def _check_telegram(self) -> Dict:
        token = self.settings.telegram_bot_token
        if not token:
            return {"check_name": "telegram_bot", "status": "warning", "message": "Telegram token not configured", "details": {}}
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"https://api.telegram.org/bot{token}/getMe")
            if r.status_code == 200:
                username = r.json().get("result", {}).get("username", "unknown")
                return {"check_name": "telegram_bot", "status": "ok", "message": f"Bot @{username} connected", "details": {}}
            return {"check_name": "telegram_bot", "status": "warning", "message": f"HTTP {r.status_code}", "details": {}}
        except Exception as exc:
            return {"check_name": "telegram_bot", "status": "error", "message": str(exc), "details": {}}

    async def _check_backend(self) -> Dict:
        return {"check_name": "backend_process", "status": "ok", "message": "Backend process running", "details": {}}

    async def _check_disk(self) -> Dict:
        try:
            disk = shutil.disk_usage("/")
            percent = disk.used / disk.total * 100
            status = "ok" if percent < 80 else "warning" if percent < 90 else "error"
            return {
                "check_name": "disk_usage",
                "status": status,
                "message": f"Disk {percent:.1f}% used",
                "details": {
                    "total_gb": round(disk.total / 1e9, 1),
                    "used_gb": round(disk.used / 1e9, 1),
                    "free_gb": round(disk.free / 1e9, 1),
                    "percent": round(percent, 1),
                },
            }
        except Exception as exc:
            return {"check_name": "disk_usage", "status": "error", "message": str(exc), "details": {}}

    async def _check_memory(self) -> Dict:
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
            mem_total = next((l for l in lines if l.startswith("MemTotal:")), None)
            mem_available = next((l for l in lines if l.startswith("MemAvailable:")), None)
            if mem_total and mem_available:
                total_kb = int(mem_total.split()[1])
                available_kb = int(mem_available.split()[1])
                used_kb = total_kb - available_kb
                percent = used_kb / total_kb * 100
                status = "ok" if percent < 80 else "warning" if percent < 90 else "error"
                return {
                    "check_name": "memory_usage",
                    "status": status,
                    "message": f"Memory {percent:.1f}% used",
                    "details": {
                        "total_gb": round(total_kb / 1e6, 1),
                        "used_gb": round(used_kb / 1e6, 1),
                        "available_gb": round(available_kb / 1e6, 1),
                        "percent": round(percent, 1),
                    },
                }
            return {"check_name": "memory_usage", "status": "warning", "message": "Could not parse /proc/meminfo", "details": {}}
        except Exception as exc:
            return {"check_name": "memory_usage", "status": "error", "message": str(exc), "details": {}}

    async def _check_scheduler(self) -> Dict:
        try:
            from app.scheduler import scheduler
            jobs = scheduler.get_jobs()
            return {
                "check_name": "scheduler_jobs",
                "status": "ok" if scheduler.running else "error",
                "message": f"Scheduler running with {len(jobs)} jobs" if scheduler.running else "Scheduler not running",
                "details": {"job_ids": [j.id for j in jobs]},
            }
        except Exception as exc:
            return {"check_name": "scheduler_jobs", "status": "error", "message": str(exc), "details": {}}

    async def _check_pipeline_tickets(self) -> Dict:
        try:
            result = await self.db.execute(select(func.count(Ticket.id)))
            ticket_count = result.scalar()
            result = await self.db.execute(
                select(func.count(Ticket.id)).where(Ticket.status == "error")
            )
            error_count = result.scalar()
            result = await self.db.execute(
                select(func.count(PipelineTrace.id)).where(PipelineTrace.status == "error")
            )
            trace_errors = result.scalar()

            status = "error" if trace_errors > 0 or error_count > 5 else "ok"
            return {
                "check_name": "ticket_pipeline",
                "status": status,
                "message": f"{ticket_count} tickets, {error_count} errors, {trace_errors} trace errors",
                "details": {"ticket_count": ticket_count, "error_count": error_count, "trace_errors": trace_errors},
            }
        except Exception as exc:
            return {"check_name": "ticket_pipeline", "status": "error", "message": str(exc), "details": {}}

    async def _check_pipeline_finance(self) -> Dict:
        try:
            result = await self.db.execute(select(func.count(Ticket.id)))
            ticket_count = result.scalar()
            status = "ok" if ticket_count > 0 else "warning"
            return {
                "check_name": "finance_pipeline",
                "status": status,
                "message": f"Finance analysis ready ({ticket_count} tickets in DB)",
                "details": {"ticket_count": ticket_count},
            }
        except Exception as exc:
            return {"check_name": "finance_pipeline", "status": "error", "message": str(exc), "details": {}}

    async def _check_pipeline_warranty(self) -> Dict:
        try:
            result = await self.db.execute(
                select(func.count(Product.id)).where(Product.has_warranty == True)
            )
            warranty_count = result.scalar()
            return {
                "check_name": "warranty_pipeline",
                "status": "ok",
                "message": f"{warranty_count} warrantied products tracked",
                "details": {"warranty_count": warranty_count},
            }
        except Exception as exc:
            return {"check_name": "warranty_pipeline", "status": "error", "message": str(exc), "details": {}}

    async def _check_pipeline_shopping(self) -> Dict:
        try:
            result = await self.db.execute(select(func.count(ConsumptionCycle.id)))
            cycle_count = result.scalar()
            result = await self.db.execute(select(func.count(ShoppingList.id)))
            list_count = result.scalar()
            return {
                "check_name": "shopping_pipeline",
                "status": "ok",
                "message": f"{cycle_count} consumption cycles, {list_count} shopping lists",
                "details": {"consumption_cycles": cycle_count, "shopping_lists": list_count},
            }
        except Exception as exc:
            return {"check_name": "shopping_pipeline", "status": "error", "message": str(exc), "details": {}}

    async def _check_pipeline_storage(self) -> Dict:
        configured = all([
            self.settings.google_client_id,
            self.settings.google_client_secret,
            self.settings.google_refresh_token,
        ])
        return {
            "check_name": "storage_config",
            "status": "ok" if configured else "warning",
            "message": "Google Drive configured" if configured else "Google Drive not fully configured",
            "details": {"drive_configured": configured},
        }

    async def _check_pipeline_agents(self) -> Dict:
        key = self.settings.openrouter_api_key or ""
        if not key.startswith("sk-or-v1-"):
            return {"check_name": "agents_llm", "status": "error", "message": "Agents cannot run without OpenRouter key", "details": {}}
        return {
            "check_name": "agents_llm",
            "status": "ok",
            "message": "Agents LLM backend available",
            "details": {"model_default": "openai/gpt-4o-mini"},
        }

    async def get_recent_readings(self, minutes: int = 60) -> List[Dict]:
        """Return recent sensor readings grouped by component."""
        since = datetime.utcnow() - timedelta(minutes=minutes)
        result = await self.db.execute(
            select(SensorReading)
            .where(SensorReading.created_at >= since)
            .order_by(SensorReading.created_at.desc())
        )
        readings = result.scalars().all()
        return [
            {
                "id": r.id,
                "component": r.component,
                "check_name": r.check_name,
                "status": r.status,
                "message": r.message,
                "details": r.details,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in readings
        ]

    async def get_latest_by_component(self) -> Dict[str, Dict]:
        """Return the most recent reading per component."""
        # Subquery: max created_at per component
        subq = select(
            SensorReading.component,
            func.max(SensorReading.created_at).label("max_created")
        ).group_by(SensorReading.component).subquery()

        result = await self.db.execute(
            select(SensorReading)
            .join(
                subq,
                (SensorReading.component == subq.c.component)
                & (SensorReading.created_at == subq.c.max_created),
            )
        )
        latest = {}
        for r in result.scalars().all():
            latest[r.component] = {
                "check_name": r.check_name,
                "status": r.status,
                "message": r.message,
                "details": r.details,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
        return latest

    async def get_pipeline_traces(self, limit: int = 50) -> List[Dict]:
        """Return recent pipeline traces."""
        result = await self.db.execute(
            select(PipelineTrace)
            .order_by(PipelineTrace.created_at.desc())
            .limit(limit)
        )
        return [
            {
                "id": t.id,
                "step": t.step,
                "status": t.status,
                "ticket_id": t.ticket_id,
                "user_id": t.user_id,
                "duration_ms": t.duration_ms,
                "details": t.details,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in result.scalars().all()
        ]

    async def get_metrics(self) -> Dict:
        """Return key system metrics."""
        result = await self.db.execute(select(func.count(Ticket.id)))
        ticket_count = result.scalar()
        result = await self.db.execute(select(func.count(Product.id)))
        product_count = result.scalar()
        result = await self.db.execute(select(func.count(ProcessingError.id)))
        error_count = result.scalar()
        result = await self.db.execute(select(func.count(PipelineTrace.id)))
        trace_count = result.scalar()

        # Last 24h
        since = datetime.utcnow() - timedelta(hours=24)
        result = await self.db.execute(
            select(func.count(Ticket.id)).where(Ticket.created_at >= since)
        )
        tickets_24h = result.scalar()

        return {
            "tickets_total": ticket_count,
            "products_total": product_count,
            "errors_total": error_count,
            "traces_total": trace_count,
            "tickets_last_24h": tickets_24h,
            "timestamp": datetime.utcnow().isoformat(),
        }
