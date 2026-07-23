# AGENTS.md — Iztack-Finance

Agent-focused guide for working on the Iztack-Finance codebase.

## Project purpose

Iztack-Finance is a personal/family finance assistant that:
- Extracts data from shopping receipts via OCR + LLM vision.
- Requests CFDI invoices automatically from store portals.
- Tracks expenses, warranties, and smart shopping lists.
- Provides fiscal/financial advice via specialized AI agents.
- Sends notifications through Telegram.

## Active architecture

The live code lives in two main folders:

```
backend/     FastAPI + SQLAlchemy 2 async + Pydantic v2
frontend/    Next.js 15 + Tailwind CSS
```

Legacy folders (`apps/`, `packages/`, `infrastructure/`) have been removed. Do not reintroduce them.

### Backend layout

```
backend/app/
  main.py              FastAPI entry point, CORS, lifespan, router registration
  config.py            Pydantic-Settings based configuration
  database/
    connection.py      async + sync engines, session helpers
    models.py          single source of truth for SQLAlchemy models
  modules/             domain modules
    auth/              JWT user authentication
    admin_staff/       admin portal authentication
    settings/          user settings (Telegram, Google Drive)
    ocr/               receipt OCR pipeline
    tickets/           ticket upload, multi-image handling, persistence
    facturacion/       CFDI invoice automation
    finanzas/          financial analysis & reports
    garantias/         warranty tracking
    shopping_list/     smart shopping lists
    almacenamiento/    Google Drive integration
    clasificacion/     product classification
    monitoring/        sensors, alerts, dashboard
    chat/              in-app chat
    dashboard/         dashboard data endpoints
    fiscal/            fiscal endpoints
    agents/            multi-agent orchestration endpoints
    business/          family business tracking
    setup/             onboarding wizard
    bots/telegram_bot.py   Telegram bot
  scheduler.py         APScheduler jobs (daily/weekly/warranty/sensors/invoices)
  utils/               crypto, hashing, LLM client, validators, setup crypto
```

### Frontend layout

```
frontend/
  app/                 Next.js App Router pages
  components/          React components
  lib/                 API clients and helpers
  public/              static assets
  next.config.js       standalone output, API rewrites
```

## Key conventions

- Python 3.12+ compatible. Requirements were updated for Python 3.13 compatibility where possible.
- Use `async` SQLAlchemy sessions (`AsyncSession`) for FastAPI endpoints.
- Sync sessions (`SyncSession`) are only for scheduler tasks and the Telegram bot.
- All sensitive data is encrypted at rest using `CryptoManager` (PBKDF2 + AES-256-GCM) or `setup_crypto` (AES-256-GCM with a master key file).
- Do not write secrets to `.env` from application code. The setup wizard persists them encrypted in the `tenants` table.
- Routes should use Pydantic request schemas instead of raw `dict` bodies.
- Module routers are registered in `backend/app/main.py`.
- New SQLAlchemy models go in `backend/app/database/models.py`.

## Environment variables

Copy `.env.example` to `.env` and fill at least:

- `SECRET_KEY` — JWT / crypto master secret (persist between restarts).
- `OPENROUTER_API_KEY` — LLM provider key.
- `DATABASE_URL` / `DATABASE_SYNC_URL` — PostgreSQL URLs.
- `REDIS_URL` — Redis connection.
- `ALLOWED_ORIGINS` — CORS origins (includes `https://finance.iztack.com`, `https://api.iztack.com`, `https://admfinance.iztack.com`).
- `SMTP_*` / `ADMIN_ALERT_EMAILS` — for monitoring email alerts.

## Running locally

```bash
# Development
docker compose up -d --build

# Production build
docker compose -f docker-compose.prod.yml up -d --build
```

Health check:

```bash
curl http://localhost:8000/api/health
```

## Testing / linting

```bash
cd backend
python -m pytest tests/

# Lint (recommended)
ruff check app/
ruff format app/
```

## Deployment

- Production target: Proxmox LXC (CT 101) with Docker.
- Cloudflare Tunnel exposes `finance.iztack.com`, `api.iztack.com`, `admfinance.iztack.com`.
- Use `docker-compose.prod.yml` for production.
- The Telegram bot container reads the encrypted bot token from the `tenants` table, not from `.env`.

## Common pitfalls

- Do not import from removed `apps/` or `packages/` folders.
- `CryptoManager` and `setup_crypto` use different key derivation schemes; do not mix them.
- After adding a new SQLAlchemy model, `Base.metadata.create_all` in `init_db` will create it on startup (no migrations yet).
- The scheduler runs inside the backend container; Celery was removed.
- Multi-image uploads without `is_continuation` now create one ticket per image.

## Contact / ownership

Project: Iztack-Finance
Production URLs:
- App: https://finance.iztack.com
- API: https://api.iztack.com
- Admin: https://admfinance.iztack.com
