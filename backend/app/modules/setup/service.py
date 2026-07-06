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
import secrets
import subprocess
from datetime import datetime
from typing import Optional

import httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Tenant
from app.modules.setup.schemas import FinalizeRequest, ValidateRequest

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

# In production this key MUST come from a KMS / env var, NEVER hardcoded.
# For local-dev / single-tenant we derive it from the SECRET_KEY env var.
def _get_or_create_master_key() -> bytes:
    """
    Returns a 32-byte master key, persisting a random one to .setup_key if needed.
    """
    env_key = os.getenv("SETUP_MASTER_KEY")
    if env_key:
        # Deterministic dev key — NOT for production.
        import hashlib
        return hashlib.sha256(env_key.encode()).digest()

    key_file = os.getenv("SETUP_MASTER_KEY_FILE", "/opt/iztack-finance/.setup_key")
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read()
    key = secrets.token_bytes(32)
    try:
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, "wb") as f:
            f.write(key)
        os.chmod(key_file, 0o600)
        logger.info("Generated new master key at %s", key_file)
    except Exception as exc:
        logger.warning("Could not persist master key (%s); using in-memory key", exc)
    return key


def encrypt_secret(plaintext: str, key: bytes, key_id: str = "v1") -> tuple[bytes, str]:
    """Encrypt with AES-256-GCM. Returns (ciphertext, key_id)."""
    aes = AESGCM(key)
    nonce = secrets.token_bytes(12)  # 96-bit nonce
    ct = aes.encrypt(nonce, plaintext.encode("utf-8"), associated_data=key_id.encode())
    return nonce + ct, key_id


# =============================================================================
# Persistence
# =============================================================================


async def is_setup_completed(db: AsyncSession) -> bool:
    """True if at least one tenant has setup_completed=True."""
    result = await db.execute(
        select(Tenant).where(Tenant.setup_completed == True).limit(1)  # noqa: E712
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
    key = _get_or_create_master_key()
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

    # Write to .env so the bot container picks it up on next restart
    _write_env_file(req, tenant.id)

    # Trigger bot restart if running in Docker
    restarted = _restart_telegram_bot()

    logger.info("Setup finalized for tenant=%s (restart_triggered=%s)", tenant.id, restarted)
    return tenant


def _write_env_file(req: FinalizeRequest, tenant_id: str) -> None:
    """
    Append/update credential lines in /opt/iztack-finance/.env (the docker-compose bind mount).
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

    existing["TELEGRAM_BOT_TOKEN"] = req.telegram_bot_token
    existing["GEMINI_API_KEY"] = req.gemini_api_key
    if req.google_client_id:
        existing["GOOGLE_CLIENT_ID"] = req.google_client_id
    if req.google_client_secret:
        existing["GOOGLE_CLIENT_SECRET"] = req.google_client_secret
    if req.google_refresh_token:
        existing["GOOGLE_REFRESH_TOKEN"] = req.google_refresh_token
    existing["DEFAULT_TENANT_ID"] = tenant_id

    with open(env_path, "w", encoding="utf-8") as f:
        f.write("# Auto-updated by /api/setup/finalize at %s\n" % datetime.utcnow().isoformat())
        for k, v in existing.items():
            f.write(f"{k}={v}\n")
    try:
        os.chmod(env_path, 0o600)
    except Exception:
        pass
    logger.info("Wrote credentials to %s", env_path)


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