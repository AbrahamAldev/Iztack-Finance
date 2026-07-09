# 🏦 Iztack-Finance

> **Tu asistente financiero automatizado.** Captura tickets con una foto, solicita facturas CFDI automáticamente, organiza tus gastos y recibe análisis financieros con IA.

[![CI](https://github.com/AbrahamAldev/Iztack-Finance/actions/workflows/ci.yml/badge.svg)](https://github.com/AbrahamAldev/Iztack-Finance/actions/workflows/ci.yml)
[![Deploy](https://github.com/AbrahamAldev/Iztack-Finance/actions/workflows/deploy-staging.yml/badge.svg)](https://github.com/AbrahamAldev/Iztack-Finance/actions/workflows/deploy-staging.yml)

---

## ✨ Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| 📸 **Captura Inteligente** | Toma una foto de tu ticket y el sistema extrae automáticamente tienda, fecha, productos y total. |
| 🤖 **Facturación Automática CFDI** | El bot accede al portal de cada tienda con tus credenciales y solicita la factura por ti. |
| 📊 **Dashboard Inteligente** | Visualiza todos tus gastos en tiempo real con gráficos interactivos. Detecta fugas de dinero. |
| 🛒 **Lista de Compras Automática** | El sistema detecta tus ciclos de consumo y genera listas inteligentes. Comparte con tu familia. |
| 🔧 **Alertas de Garantía** | Te avisamos automáticamente cuando un producto está por vencer su garantía. |
| ☁️ **Almacenamiento en Google Drive** | Todas tus facturas PDF y XML organizadas por tienda, tipo de gasto y año. |
| 💬 **Chat con IA** | Asistente financiero con IA (DeepSeek via OpenRouter) que responde tus dudas. |
| 📱 **Multi-plataforma** | Web + Telegram. El bot @IztackFinance_Bot procesa tickets y responde al instante. |
| 🏛️ **Optimización Fiscal** | Sube tu constancia fiscal y estados de cuenta. La IA calcula deducciones personales. |
| 🔒 **Privacidad Total** | Datos cifrados con AES-256-GCM y aislados por usuario. |
| 🏪 **Multi-negocio Familiar** | Administra las finanzas de tu hogar y tus negocios por separado. |

---

## 🏗️ Stack Tecnológico

| Capa | Tecnología |
|---|---|
| **Frontend** | Next.js 14 + Tailwind CSS |
| **Backend** | FastAPI + SQLAlchemy 2 async + Pydantic v2 |
| **Base de Datos** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **Bot Telegram** | python-telegram-bot v21 (multi-usuario) |
| **IA Chat** | OpenRouter (DeepSeek free) |
| **OCR** | Google Gemini 2.0 Flash |
| **CFDI** | Playwright (9 portales) |
| **Cifrado** | AES-256-GCM (PBKDF2) |
| **Infraestructura** | Proxmox LXC + Docker |
| **Túnel** | Cloudflare Tunnel |
| **CI/CD** | GitHub Actions |

---

## 🚀 Inicio Rápido

```bash
# Clonar el repositorio
git clone git@github.com:AbrahamAldev/Iztack-Finance.git
cd Iztack-Finance

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus claves (SECRET_KEY, TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, etc.)

# Iniciar servicios
docker compose up -d --build

# Verificar
curl http://localhost:8000/api/health
# → {"status": "healthy", ...}
```

---

## 📂 Estructura del Proyecto

```
/
├── backend/                    # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── main.py            # Entry point
│   │   ├── database/          # Modelos + conexión
│   │   ├── modules/           # Módulos por dominio
│   │   │   ├── auth/          # Login/Signup JWT
│   │   │   ├── bots/          # Telegram multi-usuario
│   │   │   ├── chat/          # Chat IA (OpenRouter)
│   │   │   ├── ocr/           # OCR (Gemini)
│   │   │   ├── facturacion/   # 9 portales CFDI
│   │   │   ├── tickets/       # Upload + stitching
│   │   │   ├── finanzas/      # Análisis financiero
│   │   │   ├── garantias/     # Gestión de garantías
│   │   │   ├── shopping_list/ # Lista de compras
│   │   │   ├── settings/      # Configuración usuario
│   │   │   └── setup/         # Setup wizard
│   │   └── utils/             # Crypto, hashing, LLM
│   └── requirements.txt
├── frontend/                   # Next.js 14
│   └── app/
│       ├── page.tsx           # Landing page SaaS
│       ├── login/register/    # Autenticación
│       ├── dashboard/         # Dashboard protegido
│       ├── settings/          # Configuración
│       └── shopping-list/     # Lista de compras
├── docker-compose.yml         # 5 servicios
└── docs/                      # Documentación
```

---

## 📚 Documentación

| Documento | Propósito |
|---|---|
| [IDEA-ORIGINAL.md](docs/IDEA-ORIGINAL.md) | Visión fundacional del proyecto |
| [ARQUITECTURA_FINAL_v2.md](docs/ARQUITECTURA_FINAL_v2.md) | Arquitectura y stack actual |
| [CHANGELOG.md](docs/CHANGELOG.md) | Historial de cambios |
| [GUIA_DEPLOY_PASO_A_PASO.md](docs/GUIA_DEPLOY_PASO_A_PASO.md) | Tutorial para principiantes |
| [GUIA_ACCESO_REMOTO.md](docs/GUIA_ACCESO_REMOTO.md) | Acceso remoto seguro |

---

## 🌐 URLs

| Servicio | URL |
|---|---|
| App usuarios | [https://finance.iztack.com](https://finance.iztack.com) |
| API | [https://apifinance.iztack.com](https://apifinance.iztack.com) |
| Admin staff | [https://admfinance.iztack.com](https://admfinance.iztack.com) (próximamente) |

---

## 🔐 Seguridad

- **Cifrado:** AES-256-GCM con PBKDF2 (100K iteraciones) para credenciales de portales
- **Auth:** JWT + bcrypt para autenticación de usuarios
- **Aislamiento:** Cada usuario tiene sus datos separados por `user_id`
- **IA segura:** System prompt fijo anti-prompt-injection que nunca revela código, claves o arquitectura interna
- **Túnel:** Cloudflare Tunnel con TLS 1.3, sin puertos abiertos

---

## 👨‍💻 Desarrollo

```bash
# Tests
cd backend && python -m pytest tests/

# Lint
cd backend && flake8 app/

# Build frontend
cd frontend && npm run build
```

---

## 📄 Licencia

Este es un proyecto privado. Todos los derechos reservados.

---

<p align="center">Hecho con ❤️ en México</p>