# 🏗️ Sistema Finanzas MX — Arquitectura Final v2

## Estado del Proyecto — 19/06/2026

```
sistema-finanzas-mx/
├── apps/
│   ├── web/              Next.js 15 + shadcn/ui (desarrollo)
│   ├── bot/              Telegram Bot (código migrado)
│   ├── api/              FastAPI + routers por dominio (parcial)
│   ├── worker/           ARQ + 7 tareas + scheduler ✅
│   └── cfdi/portales/    9 portales CFDI migrados ✅
├── packages/
│   ├── shared/           Modelos SQLAlchemy v2 (18 tablas) ✅
│   ├── storage/          Local + Sensitive + Email + Retention ✅
│   ├── llm/              Tesseract + OpenRouter (pendiente)
│   ├── printer/          ESC/POS (pendiente)
│   └── analytics/        Ciclos + fugas (código migrado)
├── infrastructure/
│   ├── docker-compose.yml    Caddy + 7 servicios ✅
│   ├── caddy/Caddyfile       HTTPS automático ✅
│   ├── docker/               Dockerfiles (pendientes)
│   └── scripts/              Backup, restore (pendientes)
├── docs/
│   ├── ARQUITECTURA_FINAL_v2.md  ← ESTE DOCUMENTO
│   ├── HISTORICO_ARQUITECTURA_v1.md ✅
│   └── INFRAESTRUCTURA.md ✅
├── .github/workflows/
│   ├── ci.yml ✅
│   ├── deploy-staging.yml ✅
│   └── deploy-production.yml ✅
└── frontend/ (legado v1 - migrar a apps/web/)
```

## Almacenamiento (Plan Maestro)

```
┌─────────────────────────────────────────────────────────┐
│                ARQUITECTURA DE ALMACENAMIENTO            │
├──────────────┬──────────┬───────────────────────────────┤
│    DISCO     │ TAMAÑO   │            USO                │
├──────────────┼──────────┼───────────────────────────────┤
│ SSD (sda)    │ 128 GB   │ Sistema Proxmox + raíz de CTs │
│ HDD (sdb)    │ 2 TB     │ NAS portátil (exFAT)          │
│ HDD (sdf)    │ 1 TB     │ Datos fríos para contenedores │
└──────────────┴──────────┴───────────────────────────────┘
```

- **Datos Calientes (SSD):** Exclusivo para sistema Proxmox y discos raíz de VMs/CTs
- **Datos Fríos (HDD 1TB):** Almacenamiento masivo para contenedores mediante mount points
- **NAS Portátil (HDD 2TB exFAT):** Compatible con Windows/macOS, futuro mirror con rsync

## Stack Tecnológico Definitivo

| Capa | Tecnología | Estado |
|------|-----------|--------|
| **Frontend** | Next.js 15 + Tailwind + shadcn/ui | ⏳ Migrando |
| **Backend** | FastAPI + SQLAlchemy 2 async + Pydantic v2 | ✅ Listo |
| **Bot** | python-telegram-bot v21 async | ✅ Listo |
| **Workers** | ARQ sobre Redis (3 colas) | ✅ Listo |
| **Scheduler** | ARQ Scheduler (reemplaza Celery Beat) | ✅ Listo |
| **DB** | PostgreSQL 16 (18 tablas) | ✅ Listo |
| **Cache/Cola** | Redis 7 con AOF | ✅ Listo |
| **OCR primario** | Tesseract 5 local | ⏳ Pendiente |
| **OCR fallback** | OpenRouter free (Gemini/Llama) | ⏳ Pendiente |
| **Storage local** | LocalStorage + SensitiveStorage | ✅ Listo |
| **Storage nube** | Google Drive + Dropbox + OneDrive | ⏳ Pendiente |
| **Email fallback** | EmailStorage (ZIP mensual) | ✅ Listo |
| **Retención** | RetentionManager (13 meses) | ✅ Listo |
| **CFDI** | Playwright (9 portales) | ✅ Listo |
| **Proxy** | Caddy (HTTPS automático) | ✅ Listo |
| **CI/CD** | GitHub Actions (3 pipelines) | ✅ Listo |

## Flujo CI/CD

```
🧑‍💻 git push a feature/*
   → GitHub Actions: Tests + Lint + Build
   
🧑‍💻 git push a develop
   → Deploy automático a MINI PC (staging)
   → Pruebas con DB de prueba
   
🧑‍💻 git checkout main → git merge develop
   → Backup DB automático
   → Deploy a HOSTINGER
   → Health checks post-deploy
   → Notificación email/Telegram
   → Rollback automático si falla
```

## Una línea para deploy

```bash
# Subir cambios a staging
git push origin develop

# Cuando todo funcione, pasar a producción
git checkout main && git merge develop && git push origin main
```

## Servicios Docker

| Servicio | Puerto | Propósito |
|----------|--------|-----------|
| Caddy | 443 | Reverse proxy HTTPS |
| PostgreSQL | 5432 | Base de datos |
| Redis | 6379 | Cache + cola ARQ |
| API | 8000 | FastAPI |
| Worker | — | ARQ tareas async |
| Bot | — | Telegram |
| Web | 3000 | Next.js |
| Adminer | 8080 | DB inspector |