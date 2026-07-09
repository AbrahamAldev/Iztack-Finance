# 🧠 Memoria Colectiva - Iztack-Finance

> **Propósito:** Documento de contexto compartido para múltiples IAs trabajando en el proyecto.
> **Última actualización:** 2026-07-08

---

## 📋 Estado Actual del Proyecto

| Elemento | Valor |
|---|---|
| **Branch activo** | `develop` |
| **Último commit** | `ce2bca9` (feat(telegram): Fase 5 - Bot multi-usuario) |
| **URL producción** | https://finance.iztack.com |
| **URL API** | https://api.iztack.com |
| **Proxmox** | CT 101 (app) + CT 103 (tunnel) |
| **IA activa** | ✅ OpenRouter (DeepSeek free) configurado |
| **Bot Telegram** | ✅ @IztackFinance_Bot activo y multi-usuario |

---

## 🏗️ Arquitectura Actual

```
Usuario → Cloudflare (Access @iztack.com) → Cloudflare Tunnel → CT 101 (Docker)
                                                              ├── sf-backend (FastAPI :8000)
                                                              ├── sf-frontend (Next.js :3000)
                                                              ├── sf-postgres (:5432)
                                                              ├── sf-redis (:6379)
                                                              └── sf-telegram-bot (polling)
```

### Componentes principales

| Componente | Tecnología | Puerto |
|---|---|---|
| Backend API | FastAPI + SQLAlchemy + PostgreSQL | 8000 |
| Frontend | Next.js 14 (App Router) + Tailwind | 3000 |
| Bot Telegram | python-telegram-bot (polling) | - |
| Túnel | Cloudflare Tunnel (efímero, token) | - |
| Almacenamiento | Google Drive (por usuario) | - |
| IA Chat | OpenRouter (DeepSeek free) | - |
| OCR | Google Gemini 2.0 Flash | - |
| CFDI | Playwright (9 portales) | - |

### Infraestructura Proxmox

| CT | Hostname | IP | Propósito |
|---|---|---|---|
| 101 | iztack-finance | 192.168.0.106 | Docker (app) |
| 103 | cloudflare-tunnel | 192.168.0.107 | cloudflared |

---

## ✅ Módulos Completados (Fases 1-5)

- [x] **Login/Signup** — JWT, /login, /register (Fase 1)
- [x] **Landing page SaaS** — Features, pricing, CTA
- [x] **Rutas protegidas** — AuthGuard en dashboard, settings, shopping-list
- [x] **Settings** — Telegram chat_id + Google Drive por usuario (Fase 2)
- [x] **Subida de tickets** — Cámara con overlay guía + stitching multi-imagen (Fase 3)
- [x] **Chat IA** — OpenRouter DeepSeek free, anti-prompt-injection (Fase 4)
- [x] **Telegram multi-usuario** — @IztackFinance_Bot para todos (Fase 5)
- [x] **OCR** — Extracción de datos con Gemini
- [x] **Facturación CFDI** — 9 portales (Liverpool, IKEA, Walmart, Amazon, etc.)
- [x] **Clasificación** — Productos por categoría y tipo de gasto
- [x] **Garantías** — Detección automática de productos con garantía
- [x] **Lista de compras** — Modelos y lógica base
- [x] **Análisis financiero** — Modelos y lógica base
- [x] **Google Drive** — Almacenamiento de PDF/XML
- [x] **Setup wizard** — Configuración inicial
- [x] **CI/CD** — GitHub Actions con appleboy/ssh-action
- [x] **Infraestructura** — Proxmox, Cloudflare Tunnel, dominio

---

## 🔄 Funcionalidades Pendientes (de la visión original)

### Prioridad Alta

| # | Funcionalidad | Docs relacionados | Descripción |
|---|---|---|---|
| 1 | **Dashboard con datos reales** | IDEA-ORIGINAL.md §4 | Hoy muestra $0 en todos los KPIs. Conectar con tickets reales de la DB |
| 2 | **Lista de compras inteligente** | IDEA-ORIGINAL.md §5 | Detección de ciclos de consumo, aprobación familiar, impresión térmica |
| 3 | **Análisis financiero** | IDEA-ORIGINAL.md §4 | Detección de fugas de dinero, proyecciones, recomendaciones de ahorro |
| 4 | **Flujo completo de facturación** | IDEA-ORIGINAL.md §2 | Creación automática de cuentas, búsqueda en Gmail, manejo de errores |
| 5 | **Workers ARQ + scheduler** | TASK-LIST.md | Tareas programadas (análisis diario, lista semanal, reporte mensual) |

### Prioridad Media

| # | Funcionalidad | Docs relacionados | Descripción |
|---|---|---|---|
| 6 | **Multi-negocio familiar** | IDEA-ORIGINAL.md §6 | CRUD de negocios, API para POS, dashboards por negocio |
| 7 | **Más portales CFDI** | TASK-LIST.md Fase 3 | Costco, Chedraui, Sam's Club, Soriana |
| 8 | **Mejora OCR** | TASK-LIST.md Fase 1 | Tesseract 5 como primario, mejor parser de tickets MX |
| 9 | **Testing** | TASK-LIST.md Testing | Tests de OCR, API, E2E, cifrado |
| 10 | **Scripts de backup/restore** | TASK-LIST.md Infra | Backup automático de DB, rotación de logs |

### Prioridad Baja

| # | Funcionalidad | Docs relacionados | Descripción |
|---|---|---|---|
| 11 | **Módulo Fiscal (México)** | IDEA-ORIGINAL.md §7 | Constancia fiscal, estados de cuenta, deducciones |
| 12 | **Impresora térmica** | IDEA-ORIGINAL.md §5 | ESC/POS USB y Bluetooth para listas de compras |
| 13 | **Pre-orden en línea** | IDEA-ORIGINAL.md §5 | Adapter de Amazon México, generar link de carrito |
| 14 | **Modo oscuro/claro** | TASK-LIST.md Frontend | next-themes |
| 15 | **PWA instalable** | TASK-LIST.md Frontend | Manifest + service worker |

---

## 📂 Estructura del Proyecto

```
/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings / env vars
│   │   ├── database/
│   │   │   ├── connection.py    # SQLAlchemy async + sync engines
│   │   │   └── models.py        # 20+ tablas
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
│   │       ├── crypto.py        # AES-256-GCM
│   │       ├── hashing.py       # bcrypt
│   │       └── llm.py           # OpenRouter client
│   ├── bot_main.py              # Telegram bot entry point
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Landing page SaaS
│   │   ├── login/               # Login
│   │   ├── register/            # Register
│   │   ├── dashboard/           # Dashboard (protegido)
│   │   ├── settings/            # Settings (Telegram + Drive)
│   │   ├── setup/               # Setup wizard
│   │   └── shopping-list/       # Shopping lists
│   └── components/
│       ├── AuthGuard.tsx        # Route protection
│       ├── AppNav.tsx           # App navigation
│       ├── ChatWidget.tsx       # AI chat bubble
│       └── TicketUpload.tsx     # Camera + upload
├── docker-compose.yml
├── .github/workflows/
│   ├── ci.yml
│   ├── deploy-staging.yml
│   └── deploy-production.yml
└── docs/
    ├── MEMORIA_IA.md             ← Este documento
    ├── ARQUITECTURA_FINAL_v2.md
    ├── CHANGELOG.md
    └── ...
```

---

## 🤖 Reglas para IAs

1. **NO modificar código de otro módulo sin preguntar** al usuario o documentarlo aquí
2. **Actualizar este documento** al completar una tarea (fecha + cambios)
3. **Usar `user_id`** en todas las queries (aislamiento multi-usuario)
4. **Commit con mensaje descriptivo** + mención del módulo afectado
5. **Revisar `models.py`** antes de crear nuevos modelos (evitar duplicados)
6. **No romper compatibilidad** con el bot de Telegram al modificar el backend
7. **Actualizar `requirements.txt`** si se agregan nuevas dependencias Python
8. **Actualizar `frontend/package.json`** si se agregan nuevas dependencias JS
9. **Mantener estilo consistente:** FastAPI async, Next.js App Router, Tailwind CSS
10. **Probar localmente antes de hacer commit** (curl al backend, build del frontend)

---

## 📝 Historial de Cambios

| Fecha | IA | Cambio |
|---|---|---|
| 2026-07-07 | Cline | Creación del documento. Estado post-deploy con túnel funcional. |
| 2026-07-07 | Cline | Fase 1: Login/Signup con JWT. |
| 2026-07-07 | Cline | Landing page SaaS + rutas protegidas + CI/CD corregido. |
| 2026-07-07 | Cline | Fase 2: Settings (Telegram + Google Drive). |
| 2026-07-08 | Cline | Fase 3: Subida de tickets con cámara y stitching. |
| 2026-07-08 | Cline | Fase 4: Chat en la app con IA real (OpenRouter DeepSeek free). |
| 2026-07-08 | Cline | Fase 5: Telegram multi-usuario (@IztackFinance_Bot). |
| 2026-07-08 | Cline | Documentación actualizada con estado real del proyecto. |