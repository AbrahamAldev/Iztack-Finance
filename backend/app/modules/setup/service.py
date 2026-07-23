"""
Sistema Financiero - Setup Service
Business logic for the onboarding wizard.

Responsibilities:
- Validate each provider's credential live (without persisting).
- Encrypt secrets with AES-256-GCM before storing them.
- Persist the Tenant row + link chat_id (optional).
- Trigger a graceful restart of the telegram-bot container so it picks up
  the new bot token. If we're not running in Docker, we just log a warning.
"""
from __future__ import annotations

import logging
import os
import re
import subprocess
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Tenant
from app.modules.setup.schemas import FinalizeRequest, ValidateRequest
from app.utils.setup_crypto import (
    encrypt_secret,
    get_or_create_master_key,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Validators (one per provider)
# =============================================================================


def _validate_telegram_shape(token: str) -> Optional[str]:
    """Return error message if malformed, None if shape looks OK."""
    if not re.match(r"^\d{6,12}:[A-Za-z0-9_-]{30,50}$", token):
        return "El token no parece válido. Formato esperado: <id>:<secret> (ej. 123456789:AAH...)."
    return None


async def validate_telegram(token: str) -> tuple[bool, str]:
    """Hit the Telegram getMe endpoint to confirm the token is alive."""
    shape_err = _validate_telegram_shape(token)
    if shape_err:
        return False, shape_err
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"https://api.telegram.org/bot{token}/getMe")
        if r.status_code != 200:
            return False, "Telegram rechazó el token (credenciales incorrectas)."
        data = r.json()
        if not data.get("ok"):
            return False, f"Telegram devolvió: {data.get('description', 'error desconocido')}"
        bot = data.get("result", {})
        name = bot.get("username", "?")
        return True, f"Conectado al bot @{name}."
    except httpx.TimeoutException:
        return False, "Telegram tardó demasiado en responder. Intenta de nuevo."
    except Exception as exc:  # pragma: no cover
        logger.exception("Telegram validation failed")
        return False, f"No se pudo contactar a Telegram: {exc}"


def _validate_gemini_shape(key: str) -> Optional[str]:
    if not key.startswith("AIza") or len(key) < 30:
        return "Las API keys de Gemini empiezan con 'AIza' y tienen ~39 caracteres."
    return None


async def validate_gemini(key: str) -> tuple[bool, str]:
    """Hit the models.list endpoint to confirm the key is alive."""
    shape_err = _validate_gemini_shape(key)
    if shape_err:
        return False, shape_err
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                "https://generativelanguage.googleapis.com/v1beta/models",
                params={"key": key, "pageSize": 1},
            )
        if r.status_code == 200:
            return True, "API key válida (modelos Gemini accesibles)."
        if r.status_code in (400, 403):
            return False, "La API key fue rechazada por Google Gemini."
        return False, f"Gemini respondió con código {r.status_code}."
    except httpx.TimeoutException:
        return False, "Gemini tardó demasiado. Intenta de nuevo."
    except Exception as exc:  # pragma: no cover
        logger.exception("Gemini validation failed")
        return False, f"No se pudo contactar a Gemini: {exc}"


async def validate_google(value: str) -> tuple[bool, str]:
    """
    Validate a Google OAuth refresh token by trying to use it.
    We need client_id + client_secret + refresh_token together to do a real call,
    so the wizard UI collects them as a single string and the service splits them.
    Format expected: "<client_id>|<client_secret>|<refresh_token>" OR a single
    refresh_token line (then client_id/secret come from .env).
    """
    parts = value.split("|")
    if len(parts) == 3:
        client_id, client_secret, refresh_token = parts
    elif len(parts) == 1 and value.startswith("ya29."):
        refresh_token = value
        client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        if not client_id or not client_secret:
            return False, "Falta client_id/secret. Pégalos como: <id>|<secret>|<token>."
    else:
        return False, "Formato: <client_id>|<client_secret>|<refresh_token> (separados por |)."

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )
        if r.status_code == 200:
            tok = r.json()
            if "access_token" in tok:
                return True, "Refresh token válido (Google OAuth funciona)."
        return False, f"Google OAuth rechazó el token (HTTP {r.status_code})."
    except Exception as exc:  # pragma: no cover
        logger.exception("Google validation failed")
        return False, f"No se pudo contactar a Google: {exc}"


VALIDATORS = {
    "telegram": validate_telegram,
    "gemini": validate_gemini,
    "google": validate_google,
}


async def validate_credential(req: ValidateRequest) -> tuple[bool, Optional[str], Optional[str]]:
    """Dispatch validation to the right provider."""
    fn = VALIDATORS.get(req.provider)
    if not fn:
        return False, None, f"Proveedor desconocido: {req.provider}"
    valid, message = await fn(req.value)
    return valid, (message if valid else None), (None if valid else message)


# =============================================================================
# Encryption (AES-256-GCM)
# =============================================================================

# =============================================================================
# Persistence
# =============================================================================


async def is_setup_completed(db: AsyncSession) -> bool:
    """True if at least one tenant has setup_completed=True."""
    result = await db.execute(
        select(Tenant).where(Tenant.setup_completed.is_(True)).limit(1)
    )
    return result.scalar_one_or_none() is not None


async def get_default_tenant(db: AsyncSession) -> Optional[Tenant]:
    """Return the first tenant (single-tenant mode)."""
    result = await db.execute(select(Tenant).order_by(Tenant.created_at.asc()).limit(1))
    return result.scalar_one_or_none()


async def finalize_setup(db: AsyncSession, req: FinalizeRequest) -> Tenant:
    """
    Create or update the default tenant with the credentials.
    Returns the Tenant row.
    """
    key = get_or_create_master_key()
    key_id = "v1"

    tenant = await get_default_tenant(db)
    if tenant is None:
        tenant = Tenant(
            name=req.tenant_name,
            timezone=req.timezone,
            currency=req.currency,
            setup_completed=False,
            encryption_key_id=key_id,
        )
        db.add(tenant)
        await db.flush()
    else:
        tenant.name = req.tenant_name
        tenant.timezone = req.timezone
        tenant.currency = req.currency
        tenant.encryption_key_id = key_id

    tenant.encrypted_telegram_bot_token = encrypt_secret(req.telegram_bot_token, key, key_id)[0]
    tenant.encrypted_gemini_api_key = encrypt_secret(req.gemini_api_key, key, key_id)[0]
    if req.google_client_id:
        tenant.encrypted_google_client_id = encrypt_secret(req.google_client_id, key, key_id)[0]
    if req.google_client_secret:
        tenant.encrypted_google_client_secret = encrypt_secret(req.google_client_secret, key, key_id)[0]
    if req.google_refresh_token:
        tenant.encrypted_google_refresh_token = encrypt_secret(req.google_refresh_token, key, key_id)[0]

    tenant.setup_completed = True
    tenant.setup_completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(tenant)

    # Persist only the non-secret tenant identifier to .env if needed by other
    # services. Actual credentials are encrypted in the database.
    _write_env_file(tenant.id)

    # Trigger bot restart if running in Docker so it loads the new token from DB
    restarted = _restart_telegram_bot()

    logger.info("Setup finalized for tenant=%s (restart_triggered=%s)", tenant.id, restarted)
    return tenant


def _write_env_file(tenant_id: str) -> None:
    """
    Persist only non-secret identifiers to .env. Secrets stay encrypted in DB.
    """
    env_path = os.getenv("ENV_FILE_PATH", "/opt/iztack-finance/.env")
    if not os.path.exists(os.path.dirname(env_path)):
        logger.warning("Cannot write env file: %s does not exist", env_path)
        return

    # Read existing
    existing: dict[str, str] = {}
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                existing[k.strip()] = v.strip()
    except FileNotFoundError:
        pass

    # Remove any previously-written secrets so they don't live in plain text
    for secret_key in (
        "TELEGRAM_BOT_TOKEN",
        "GEMINI_API_KEY",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GOOGLE_REFRESH_TOKEN",
    ):
        existing.pop(secret_key, None)

    existing["DEFAULT_TENANT_ID"] = tenant_id

    with open(env_path, "w", encoding="utf-8") as f:
        f.write("# Auto-updated by /api/setup/finalize at %s\n" % datetime.utcnow().isoformat())
        for k, v in existing.items():
            f.write(f"{k}={v}\n")
    try:
        os.chmod(env_path, 0o600)
    except Exception:
        pass
    logger.info("Wrote non-secret config to %s", env_path)


def _restart_telegram_bot() -> bool:
    """Trigger a graceful restart of the sf-telegram-bot container (best effort)."""
    try:
        # Detect if we're inside docker (/.dockerenv exists in containers)
        if not os.path.exists("/.dockerenv"):
            logger.info("Not running inside docker; skipping restart.")
            return False

        # Try via docker CLI (mounted socket)
        result = subprocess.run(
            ["docker", "compose", "-f", "/opt/iztack-finance/docker-compose.yml",
             "restart", "telegram-bot"],
            timeout=15,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            logger.info("Telegram bot container restarted.")
            return True
        logger.warning("docker compose restart failed: %s", result.stderr)
        return False
    except FileNotFoundError:
        logger.info("docker CLI not available; bot will pick up new token on next deploy.")
        return False
    except Exception as exc:  # pragma: no cover
        logger.warning("Could not restart bot: %s", exc)
        return False
