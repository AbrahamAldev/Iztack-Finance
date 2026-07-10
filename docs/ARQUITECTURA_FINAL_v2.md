# 🏗️ Iztack-Finance — Arquitectura Final v5

## Estado del Proyecto — 09/07/2026 (Fase G completada)

## Stack Tecnológico Actual

| Capa | Tecnología | Estado |
|------|-----------|--------|
| **Frontend** | Next.js 14 + Tailwind CSS | ✅ Listo |
| **Backend** | FastAPI + SQLAlchemy 2 async + Pydantic v2 | ✅ Listo |
| **Bot** | python-telegram-bot v21 async (multi-usuario) | ✅ Listo |
| **DB** | PostgreSQL 16 (20+ tablas) | ✅ Listo |
| **Cache** | Redis 7 | ✅ Listo |
| **OCR** | OpenRouter GPT-4o-mini Vision | ✅ Listo |
| **IA Chat** | OpenRouter GPT-4o-mini | ✅ Listo |
| **Auth** | JWT + bcrypt | ✅ Listo |
| **Cifrado** | AES-256-GCM (PBKDF2) | ✅ Listo |
| **Storage** | Google Drive (por usuario) | ✅ Listo |
| **CFDI Base** | Playwright (9 portales) | ✅ Listo |
| **Facturación Intel.** | Orchestrator + Learner + IA Fiscal | ✅ Listo |
| **Fiscal** | CSF, regímenes, deducciones (LISR) | ✅ Listo |
| **Workers** | APScheduler (diario, semanal, garantías) | ✅ Listo |
| **Túnel** | Cloudflare Tunnel (efímero) | ✅ Listo |
| **CI/CD** | Cron local cada 5 min | ✅ Listo |
| **Dominio** | finance.iztack.com / api.iztack.com / admfinance.iztack.com | ✅ Listo |

## Servicios Docker

| Servicio | Puerto | Propósito |
|----------|--------|-----------|
| PostgreSQL | 5432 | Base de datos |
| Redis | 6379 | Cache |
| Backend | 8000 | FastAPI + Scheduler |
| Frontend | 3000 | Next.js |
| Telegram Bot | — | Polling |
| Admin Portal | 3001 | nginx para admfinance.iztack.com |

## Módulos Implementados

| Módulo | Archivos | Estado |
|--------|---------|--------|
| Auth | `auth/` (routes, service, deps, schemas) | ✅ |
| Admin Staff | `admin_staff/` (routes, service) | ✅ |
| OCR | `ocr/` (OpenRouter Vision) | ✅ |
| Tickets | `tickets/` (upload, billing trigger) | ✅ |
| Chat IA | `chat/` (routes, service) | ✅ |
| Dashboard | `dashboard/` (routes, service con DB real) | ✅ |
| Settings | `settings/` (Telegram, Drive) | ✅ |
| Telegram Bot | `bots/telegram_bot.py` | ✅ |
| Facturación Intel. | `facturacion/` (orchestrator, discovery, learner, credential_mgr, fiscal_advisor) | ✅ |
| Finanzas | `finanzas/` (análisis, fugas, proyecciones) | ✅ |
| Business | `business/` (multi-negocio CRUD) | ✅ |
| Fiscal | `fiscal/` (CSF, regímenes, deducciones) | ✅ |
| Scheduler | `scheduler.py` (APScheduler) | ✅ |
| PWA | `public/manifest.json` | ✅ |

## Flujo CI/CD

```
git push a develop → Cron local cada 5 min (servidor) → docker compose up -d --build
```

> GitHub Actions Deploy está deshabilitado (red local inaccesible desde runners de GitHub).