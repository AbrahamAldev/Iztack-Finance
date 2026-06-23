"""
Sistema Financiero - Info Endpoint
Returns non-sensitive runtime info about the deployment.
Useful for the dashboard "Connections" widget.
"""
import logging
import platform
import sys
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/info", tags=["System"])
async def get_info(db: AsyncSession = Depends(get_db)):
    """Deployment info — exposed through Cloudflare Access (safe)."""
    db_ok = False
    try:
        result = await db.execute(text("SELECT 1"))
        db_ok = result.scalar() == 1
    except Exception as exc:
        logger.warning("DB health check failed: %s", exc)

    return {
        "app": "Sistema Financiero",
        "version": "1.1.0"  """
Sistema Financiero - Info Endpoint
Returns non-sensitive runtime info about the deployment.
Useful for the  "server_time_utc": datetime.utcnow().isoformat() + "Z",
    }
