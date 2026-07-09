# 🏗️ Iztack-Finance — Arquitectura Final v4

## Estado del Proyecto — 09/07/2026

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
│   │   │   ├── admin_staff/     # Admin Portal (admfinance.iztack.com)
│   │   │   ├── bots/            # Telegram Bot multi-usuario
│   │   │   ├── chat/            # Chat IA con OpenRouter
│   │   │   ├── dashboard/       # Dashboard con datos reales
│   │   │   ├── ocr/             # OCR (OpenRouter GPT-4o-mini Vision)
│   │   │   ├── facturacion/     # 9 portales CFDI (base)
│   │   │   │   ├── portales/    # Portales individuales
│   │   │   │   ├── email/       # Búsqueda en Gmail
│   │   │   │   ├── orchestrator.py       # ⏳ Flujo completo
│   │   │   │   ├── portal_discovery.py   # ⏳ Descubrir URL
│   │   │   │   ├── portal_learner.py     # ⏳ Aprender formularios
│   │   │   │   ├── credential_manager.py # ⏳ Gestión credenciales
│   │   │   │   ├── fiscal_advisor.py     # ⏳ Recomendaciones fiscales
│   │   │   │   └── templates/            # ⏳ Plantillas aprendidas
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
│   │       └── llm.py           # OpenRouter client (GPT-4o-mini)
│   ├── bot_main.py              # Telegram bot entry point
│   ├── test_openrouter.py       # Test de conectividad
│   └── requirements.txt
├── frontend/
│   ├── admin/                   # Admin Portal SPA
│   │   ├── index.html
│   │   └── nginx.conf
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
│       └── TicketUpload.tsx     # File upload (selector nativo)
├── docker-compose.yml           # 6 servicios (incl. admin)
├── scripts/
│   └── auto_deploy.py           # Webhook listener
├── .github/workflows/
│   ├── ci.yml
│   ├── deploy.yml               # Solo manual (workflow_dispatch)
│   ├── deploy-staging.yml
│   └── deploy-production.yml
└── docs/
    ├── MEMORIA_IA.md
    ├── ARQUITECTURA_FINAL_v2.md # ← ESTE DOCUMENTO
    ├── CHANGELOG.md
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
| **OCR** | OpenRouter GPT-4o-mini Vision | ✅ Listo |
| **IA Chat** | OpenRouter GPT-4o-mini | ✅ Listo |
| **Auth** | JWT + bcrypt | ✅ Listo |
| **Cifrado** | AES-256-GCM (PBKDF2) | ✅ Listo |
| **Storage** | Google Drive (por usuario) | ✅ Listo |
| **CFDI Base** | Playwright (9 portales) | ✅ Listo |
| **Facturación Intel.** | Orchestrator + Learner + IA Fiscal | ⏳ Pendiente |
| **Túnel** | Cloudflare Tunnel (efímero) | ✅ Listo |
| **CI/CD** | Cron local cada 5 min | ✅ Listo |
| **Dominio** | finance.iztack.com / api.iztack.com / admfinance.iztack.com | ✅ Listo |

## Servicios Docker

| Servicio | Puerto | Propósito |
|----------|--------|-----------|
| PostgreSQL | 5432 | Base de datos |
| Redis | 6379 | Cache |
| Backend | 8000 | FastAPI |
| Frontend | 3000 | Next.js |
| Telegram Bot | — | Polling |
| Admin Portal | 3001 | nginx para admfinance.iztack.com |

## Infraestructura Proxmox

| CT | Hostname | IP | Propósito |
|---|---|---|---|
| 101 | iztack-finance | 192.168.0.106 | Docker (app completa) |

## Flujo CI/CD

```
git push a develop → Cron local cada 5 min (servidor) → docker compose up -d --build
```

> GitHub Actions Deploy está deshabilitado (red local 192.168.x.x inaccesible desde runners de GitHub).

## Funcionalidades Implementadas

- [x] **Fase 0:** Admin Portal (admfinance.iztack.com, StaffUser con roles, Cloudflare Access)
- [x] **Fase 1:** Login/Signup con JWT
- [x] **Landing page:** SaaS con features, pricing, CTA
- [x] **Rutas protegidas:** AuthGuard en todas las rutas de la app
- [x] **Fase 2:** Settings (Telegram chat_id + Google Drive)
- [x] **Fase 3:** Subida de tickets (selector nativo + preview + subida, límite 5MB)
- [x] **Fase 4:** Chat IA (OpenRouter GPT-4o-mini, anti-prompt-injection)
- [x] **Fase 5:** Telegram multi-usuario (@IztackFinance_Bot)
- [x] **Fase A:** Dashboard con datos reales de DB

## Correcciones post-deploy (09/07/2026)

- [x] OCR migrado de Gemini a OpenRouter GPT-4o-mini Vision
- [x] LLM client: `model="openai/gpt-4o-mini"` (no `"free"`)
- [x] Telegram bot: corregido `SessionLocal` → `SyncSession`
- [x] ChatWidget: manejo de errores + redirección en 401
- [x] Settings: guardado de Telegram con mensajes de error claros
- [x] TicketUpload: selector nativo (sin cámara modal), 5MB límite, instrucciones
- [x] GitHub Actions Deploy: deshabilitado, auto-deploy vía cron local cada 5 min
- [x] Admin nginx: montado correctamente en sf-admin
- [x] Cloudflare Access: configurado para admfinance.iztack.com
- [x] DNS CNAME: corregido para admfinance → tunnel correcto

## ⏳ Próxima Fase: Facturación Inteligente (Fase B+)

### Flujo de facturación adaptativo:

1. **POST-OCR inmediato** — Al terminar OCR, se dispara automáticamente la facturación
2. **Secuencial** — Tickets procesados uno por uno para evitar conflictos
3. **Detección de tienda** — IA razona: ¿conocida?, ¿desconocida?, ¿conocida-pero-falló?
4. **Descubrimiento de URL** — Busca en: ticket → internet → pregunta al usuario
5. **Aprendizaje de portal** — Playwright analiza la página, mapea campos requeridos
6. **Credenciales** — Si no existen, ofrece crearlas automáticamente
7. **Datos fiscales** — Usa datos guardados del usuario; si faltan, pide solo lo necesario
8. **Tipo de gasto** — IA recomienda según régimen fiscal + buenas prácticas MX
9. **Preferencias** — Aprende de cada interacción para automatizar las siguientes
10. **Almacenamiento** — 5GB Iztack + Drive opcional (paralelo), barra de uso en dashboard
11. **Notificaciones** — Chat web + Telegram para pedir datos o informar errores
12. **Envío al email** — Opcional: enviar PDF/XML al correo al facturar (configurable en settings)

### Nuevos módulos a crear:
```
backend/app/modules/facturacion/
├── orchestrator.py         # Orquesta todo el flujo
├── portal_discovery.py     # Descubre URL de facturación
├── portal_learner.py       # Aprende estructura de páginas nuevas
├── credential_manager.py   # Crea/gestiona credenciales automáticamente
├── fiscal_advisor.py       # IA para tipo de gasto según régimen fiscal
└── templates/              # Plantillas JSON aprendidas por tienda