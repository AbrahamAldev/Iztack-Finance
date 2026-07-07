# 🧠 Memoria Colectiva - Iztack-Finance

> **Propósito:** Documento de contexto compartido para múltiples IAs trabajando en el proyecto.
> **Última actualización:** 2026-07-07

---

## 📋 Estado Actual del Proyecto

| Elemento | Valor |
|---|---|
| **Branch activo** | `develop` |
| **Último commit** | `aa6f200` (fix info.py syntax) |
| **URL producción** | https://finance.iztack.com |
| **URL API** | https://api.iztack.com |
| **Proxmox** | CT 101 (app) + CT 103 (tunnel) |

---

## 🏗️ Arquitectura

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

### Infraestructura Proxmox

| CT | Hostname | IP | Propósito |
|---|---|---|---|
| 101 | iztack-finance | 192.168.0.106 | Docker (app) |
| 103 | cloudflare-tunnel | 192.168.0.107 | cloudflared |

---

## ✅ Módulos Implementados

- [x] **OCR** — Extracción de datos de tickets desde imágenes
- [x] **Facturación** — Portales: Amazon, Walmart, Liverpool, IKEA, Home Depot, OXXO, Farmacias Similares, Pemex, BP
- [x] **Clasificación** — Productos por categoría y tipo de gasto
- [x] **Garantías** — Detección automática de productos con garantía
- [x] **Lista de compras** — Inteligente con ciclo de consumo y aprobación familiar
- [x] **Análisis financiero** — Dashboard con detección de fugas y recomendaciones
- [x] **Google Drive** — Almacenamiento de PDF/XML de facturas
- [x] **Setup wizard** — Configuración inicial del sistema
- [x] **Telegram Bot** — Recepción de tickets y comandos (multi-tenant vía chat_id)

---

## 🔄 Tareas en Progreso / Pendientes

- [x] **Login/Signup** — Autenticación con JWT (Fase 1) ✅ COMPLETADO Y DEPLOYADO
- [x] **Landing page SaaS** — Página informativa con features, pricing, CTA ✅
- [x] **Rutas protegidas** — /app/* solo accesible con JWT válido ✅
- [ ] **Settings** — Vincular Telegram chat_id + Google Drive por usuario (Fase 2)
- [ ] **Subida de tickets** — Cámara + archivos desde frontend (Fase 3)
- [ ] **Chat en la app** — Reemplazo gradual de Telegram (Fase 4)
- [ ] **Telegram multi-usuario** — Un solo bot para todos (Fase 5)
- [ ] **CI/CD** — Reparar GitHub Actions (ssh-keyscan falla por secret faltante)

---

## 📂 Estructura del Proyecto

```
/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings / env vars
│   │   ├── database/
│   │   │   ├── connection.py    # SQLAlchemy async engine
│   │   │   └── models.py        # All DB models
│   │   ├── modules/
│   │   │   ├── bots/telegram_bot.py
│   │   │   ├── ocr/             # OCR service
│   │   │   ├── facturacion/     # Portal scraping
│   │   │   ├── almacenamiento/  # Google Drive
│   │   │   ├── clasificacion/   # Product categorization
│   │   │   ├── finanzas/        # Financial analysis
│   │   │   ├── garantias/       # Warranty detection
│   │   │   ├── shopping_list/   # Smart shopping lists
│   │   │   ├── setup/           # Setup wizard
│   │   │   └── info.py          # Health endpoint
│   │   └── utils/
│   │       ├── crypto.py        # AES encryption
│   │       └── hashing.py       # Password hashing
│   ├── bot_main.py              # Telegram bot entry point
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Landing page
│   │   ├── dashboard/           # Dashboard page
│   │   ├── settings/            # Settings page
│   │   ├── setup/               # Setup wizard
│   │   └── shopping-list/       # Shopping lists
│   └── Dockerfile
├── docker-compose.yml
├── infrastructure/
├── packages/
└── docs/
    ├── MEMORIA_IA.md             ← Este documento
    ├── ARQUITECTURA_FINAL_v2.md
    ├── GUIA_DEPLOY_PASO_A_PASO.md
    ├── GUIA_CLOUDFLARE_TUNNEL.md
    └── ...
```

---

## 🧪 Cómo Ejecutar Tests

```bash
# Backend tests
cd backend && python -m pytest tests/

# Frontend build check
cd frontend && npm run build
```

---

## 🚀 Cómo Hacer Deploy

El deploy se hace automáticamente vía GitHub Actions (`.github/workflows/deploy.yml`).

Manual:
```bash
ssh proxmox pct exec 101 -- \
  "cd /opt/iztack-finance && git pull && docker compose up -d --build"
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
| 2026-07-07 | Cline | Fase 1 completada: Login/Signup con JWT. Modelo User, módulo auth, páginas /login /register, Navbar. |
