"""
Sistema Financiero - Configuration Module
Loads environment variables and provides settings for the entire application.
"""
from pydantic_settings import BaseSettings
from typing import Optional, Literal
from functools import lru_cache


class Settings(BaseSettings):
    # --- Database ---
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sistema_financiero"
    database_sync_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/sistema_financiero"

    # --- Security ---
    secret_key: str = "default-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # --- Gemini AI (OCR) ---
    gemini_api_key: Optional[str] = None

    # --- Telegram Bot ---
    telegram_bot_token: Optional[str] = None
    telegram_chat_id_authorized: Optional[str] = None

    # --- Twilio (WhatsApp) ---
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_number: Optional[str] = None

    # --- Google APIs (Gmail + Drive) ---
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_refresh_token: Optional[str] = None
    google_drive_folder_id: Optional[str] = None

    # --- Gmail ---
    gmail_sender_email: Optional[str] = None

    # --- Redis (Celery) ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Celery ---
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # --- Storage Preference ---
    storage_backend: Literal["drive", "icloud"] = "drive"

    # --- Printer ---
    printer_type: Literal["usb", "bluetooth"] = "usb"
    printer_width: int = 57
    printer_vendor_id: Optional[str] = None
    printer_product_id: Optional[str] = None
    printer_bluetooth_mac: Optional[str] = None

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000
    environment: Literal["development", "staging", "production"] = "development"

    # --- App ---
    app_name: str = "Sistema Financiero"
    app_version: str = "1.0.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Returns cached settings instance."""
    return Settings()