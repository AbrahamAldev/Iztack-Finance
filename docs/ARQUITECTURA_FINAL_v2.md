# 🏗️ Iztack-Finance — Arquitectura Final v3

## Estado del Proyecto — 08/07/2026

```
Iztack-Finance/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings / env vars
│   │   ├── database/
│   │   │   ├── connection.py    # SQLAlchemy async + sync engines
│   │   │   └── models.py        # 20+ tablas SQLAlchemy
│   │   ├── modules/
│   │   │   ├── auth/            # Login/Signup JWT
│   │   │   ├── bots/            # Telegram Bot multi-usuario
│   │   │   ├── chat/            # Chat IA con OpenRouter
│   │   │   ├── ocr/             # OCR service (Gemini)
│   │   │   ├── facturacion/     # 9 portales CFDI
│   │   │   ├── almacenamiento/  # Google Drive
│   │   │   ├── clasificacion/   # Product categorization
│   │   │   ├── finanzas/        # Financial analysis
│   │   │   ├── garantias/       # Warranty detection
│   │   │   ├── shopping_list/   # Smart shopping lists
│   │   │   ├── tickets/         # Upload + stitching
│   │   │   ├── settings/        # User settings
│   │   │   ├── setup/           # Setup wizard
│   │   │   └── info.py          # Health endpoint
│   │   └── utils/
│   │       ├── crypto.py        # AES-256-GCM encryption
│   │       ├── hashing.py       # Password hashing (bcrypt)
│   │       └── llm.py           # OpenRouter client
│   ├── bot_main.py              # Telegram bot entry point
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Landing page SaaS
│   │   ├── login/               # Login page
│   │   ├── register/            # Register page
│   │   ├── dashboard/           # Dashboard (protegido)
│   │   ├── settings/            # Settings (Telegram + Drive)
│   │   ├── setup/               # Setup wizard
│   │   └── shopping-list/       # Shopping lists
│   └── components/
│       ├── AuthGuard.tsx        # Route protection
│       ├── AppNav.tsx           # App navigation
│       ├── ChatWidget.tsx       # AI chat bubble
│       └── TicketUpload.tsx     # Camera + upload
├── docker-compose.yml           # 5 servicios
├── .github/workflows/
│   ├── ci.yml                   # Tests + Lint + Build
│   ├── deploy-staging.yml       # Deploy a Proxmox (develop)
│   └── deploy-production.yml    # Deploy a Proxmox (main)
└── docs/
    ├── MEMORIA_IA.md            # Memoria colectiva para IAs
    ├── ARQUITECTURA_FINAL_v2.md # ← ESTE DOCUMENTO
    ├── CHANGELOG.md             # Historial de cambios
    └── ...
```

## Stack Tecnológico Actual

| Capa | Tecnología | Estado |
|------|-----------|--------|
| **Frontend** | Next.js 14 + Tailwind CSS | ✅ Listo |
| **Backend** | FastAPI + SQLAlchemy 2 async + Pydantic v2 | ✅ Listo |
| **Bot** | python-telegram-bot v21 async (multi-usuario) | ✅ Listo |
| **DB** | PostgreSQL 16 (20+ tablas) | ✅ Listo |
| **Cache** | Redis 7 | ✅ Listo |
| **OCR** | Google Gemini 2.0 Flash API | ✅ Listo |
| **IA Chat** | OpenRouter (DeepSeek free + fallback) | ✅ Listo |
| **Auth** | JWT + bcrypt | ✅ Listo |
| **Cifrado** | AES-256-GCM (PBKDF2) | ✅ Listo |
| **Storage** | Google Drive (por usuario) | ✅ Listo |
| **CFDI** | Playwright (9 portales) | ✅ Listo |
| **Túnel** | Cloudflare Tunnel (efímero) | ✅ Listo |
| **CI/CD** | GitHub Actions (3 pipelines) | ✅ Listo |
| **Dominio** | finance.iztack.com / api.iztack.com | ✅ Listo |

## Servicios Docker

| Servicio | Puerto | Propósito |
|----------|--------|-----------|
| PostgreSQL | 5432 | Base de datos |
| Redis | 6379 | Cache |
| Backend | 8000 | FastAPI |
| Frontend | 3000 | Next.js |
| Telegram Bot | — | Polling |

## Infraestructura Proxmox

| CT | Hostname | IP | Propósito |
|---|---|---|---|
| 101 | iztack-finance | 192.168.0.106 | Docker (app) |
| 103 | cloudflare-tunnel | 192.168.0.107 | cloudflared |

## Flujo CI/CD

```
git push a develop → GitHub Actions → appleboy/ssh-action → Proxmox CT 101
                                                              └─ docker compose up -d --build
```

## Funcionalidades Implementadas (Fases 1-5)

- [x] **Fase 1:** Login/Signup con JWT
- [x] **Landing page:** SaaS con features, pricing, CTA
- [x] **Rutas protegidas:** AuthGuard en todas las rutas de la app
- [x] **Fase 2:** Settings (Telegram chat_id + Google Drive)
- [x] **Fase 3:** Subida de tickets (cámara con overlay + stitching multi-imagen)
- [x] **Fase 4:** Chat IA (OpenRouter DeepSeek free, anti-prompt-injection)
- [x] **Fase 5:** Telegram multi-usuario (un solo bot @IztackFinance_Bot)