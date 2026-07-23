"""
Iztack-Finance - Pipeline Tracer
Saves execution traces for each step of ticket processing.
Enables debugging from admfinance.iztack.com.
"""
import logging
import time
from typing import Any, Dict, Optional

from app.database.connection import SyncSession
from app.database.models import PipelineTrace

logger = logging.getLogger(__name__)


def _close_db(db):
    """Best-effort DB session close."""
    try:
        db.close()
    except Exception:
        pass


def trace_step(
    user_id: str,
    step: str,
    status: str = "pending",
    ticket_id: str = None,
    duration_ms: int = None,
    details: Dict[str, Any] = None,
) -> Optional[str]:
    """Save a pipeline trace entry. Returns the trace ID or None on failure."""
    db = None
    try:
        db = SyncSession()
        trace = PipelineTrace(
            user_id=user_id,
            ticket_id=ticket_id,
            step=step,
            status=status,
            duration_ms=duration_ms,
            details=details or {},
        )
        db.add(trace)
        db.commit()
        trace_id = trace.id
        _close_db(db)
        return trace_id
    except Exception as e:
        logger.error(f"Failed to save trace [{step}]: {e}")
        if db:
            _close_db(db)
        return None


class TraceContext:
    """Context manager that auto-records start/end times and status."""

    def __init__(self, user_id: str, step: str, ticket_id: str = None):
        self.user_id = user_id
        self.step = step
        self.ticket_id = ticket_id
        self.start_time = None
        self.trace_id = None

    def __enter__(self):
        self.start_time = time.time()
        self.trace_id = trace_step(
            user_id=self.user_id,
            step=self.step,
            ticket_id=self.ticket_id,
            status="pending",
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = int((time.time() - self.start_time) * 1000)
        status = "ok" if exc_type is None else "error"

        db = None
        try:
            db = SyncSession()
            trace = db.query(PipelineTrace).filter(PipelineTrace.id == self.trace_id).first()
            if trace:
                trace.status = status
                trace.duration_ms = duration
                if exc_val:
                    trace.details = (trace.details or {}) | {"error": str(exc_val)[:500]}
                db.commit()
            _close_db(db)
        except Exception as e:
            logger.error(f"Failed to update trace [{self.step}]: {e}")
            if db:
                _close_db(db)

        return False  # Don't suppress exceptions
