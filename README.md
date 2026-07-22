# 🏦 Iztack-Finance

> **Tu asistente financiero automatizado con inteligencia multi-agente.** Captura tickets con una foto, solicita facturas CFDI automáticamente, organiza tus gastos y recibe asesoría fiscal y financiera con IA.

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
| 💬 **Chat con IA Multi-Agente** | Asistente financiero con agentes especializados vía OpenRouter (DeepSeek). |
| 🏛️ **Asesor Fiscal** | Agente especializado con biblioteca curada de fuentes oficiales (SAT, LISR). |
| 📈 **Asesor Financiero** | Agente especializado con biblioteca curada de educación financiera personal y PYMES. |
| 📱 **Multi-plataforma** | Web + Telegram. El bot @IztackFinance_Bot procesa tickets y responde al instante. |
| 🔒 **Privacidad Total** | Datos cifrados con AES-256-GCM y aislados por usuario. |
| 🏪 **Multi-negocio Familiar** | Administra las finanzas de tu hogar y tus negocios por separado. |

---

## 🤖 Arquitectura Multi-Agente

Iztack-Finance implementa un sistema de agentes especializados coordinados por un orquestador:

| Agente | Rol | Modelo |
|--------|-----|--------|
| **OrchestratorAgent** | Coordina el flujo de trabajo entre agentes | DeepSeek Chat |
| **OCRAgent** | Extrae datos de tickets de compra | GPT-4o-mini / DeepSeek |
| **ChatAgent** | Atiende conversaciones y deriva a especialistas | DeepSeek Chat |
| **ValidatorAgent** | Valida coherencia de datos OCR | DeepSeek Chat |
| **BillingAgent** | Gestiona facturación CFDI automática | DeepSeek Chat |
| **LibrarianAgent** | Organiza y guarda documentos PDF/XML | Lógica Python |
| **FiscalAdvisorAgent** | Asesoría fiscal con RAG sobre biblioteca curada | DeepSeek Pro / Claude 3.5 Sonnet |
| **FinancialAdvisorAgent** | Análisis financiero con RAG sobre biblioteca curada | DeepSeek Pro / Claude 3.5 Sonnet |

Las bibliotecas de conocimiento se encuentran en `docs/agents/fiscal_library/` y `docs/agents/financial_library/`.

> **Nota:** La arquitectura multi-agente se está desarrollando activamente en el branch `multiagentes`.

---

## 🏗️ Stack Tecnológico

| Capa | Tecnología |
|---|---|
| **Frontend** | Next.js 14 + Tailwind CSS |
| **Backend** | FastAPI + SQLAlchemy 2 async + Pydantic v2 |
| **Base de Datos** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **Bot Telegram** | python-telegram-bot v21 (multi-usuario) |
| **IA / LLM** | OpenRouter (DeepSeek) |
| **OCR** | OpenRouter GPT-4o-mini Vision / DeepSeek |
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

# Cambiar al branch de multi-agentes
git checkout multiagentes

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus claves (SECRET_KEY, TELEGRAM_BOT_TOKEN, OPENROUTER_API_KEY, etc.)

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
│   │   ├── agents/            # Sistema multi-agente
│   │   │   ├── base.py        # Clases base de agentes
│   │   │   ├── orchestrator.py
│   │   │   ├── ocr_agent.py
│   │   │   ├── chat_agent.py
│   │   │   ├── validator_agent.py
│   │   │   ├── billing_agent.py
│   │   │   ├── librarian_agent.py
│   │   │   ├── fiscal_agent.py
│   │   │   ├── financial_agent.py
│   │   │   └── rag/           # Motor RAG simple
│   │   ├── database/          # Modelos + conexión
│   │   ├── modules/           # Módulos por dominio
│   │   └── utils/             # Crypto, hashing, LLM
│   └── requirements.txt
├── frontend/                   # Next.js 14
│   └── app/
│       ├── page.tsx           # Landing page SaaS
│       ├── login/register/    # Autenticación
│       ├── dashboard/         # Dashboard protegido
│       ├── settings/          # Configuración
│       └── shopping-list/     # Lista de compras
├── docs/                       # Documentación
│   └── agents/                # Bibliotecas de conocimiento
│       ├── fiscal_library/
│       └── financial_library/
├── docker-compose.yml          # Servicios de desarrollo
└── README.md                   # Este archivo
```

---

## 📚 Documentación

| Documento | Propósito |
|---|---|
| [ARQUITECTURA_AGENTES.md](docs/ARQUITECTURA_AGENTES.md) | Arquitectura del sistema multi-agente |
| [ARQUITECTURA_FINAL_v2.md](docs/ARQUITECTURA_FINAL_v2.md) | Arquitectura general y stack |
| [CHANGELOG.md](docs/CHANGELOG.md) | Historial de cambios |
| [GUIA_DEPLOY_PASO_A_PASO.md](docs/GUIA_DEPLOY_PASO_A_PASO.md) | Tutorial de despliegue |
| [GUIA_ACCESO_REMOTO.md](docs/GUIA_ACCESO_REMOTO.md) | Acceso remoto seguro |

---

## 🌐 URLs

| Servicio | URL |
|---|---|
| App usuarios | [https://finance.iztack.com](https://finance.iztack.com) |
| API | [https://api.iztack.com](https://api.iztack.com) |
| Admin staff | [https://admfinance.iztack.com](https://admfinance.iztack.com) |

---

## 🔐 Seguridad

- **Cifrado:** AES-256-GCM con PBKDF2 (100K iteraciones) para credenciales de portales y APIs.
- **Auth:** JWT + bcrypt para autenticación de usuarios. El `SECRET_KEY` persiste entre reinicios.
- **Aislamiento:** Cada usuario tiene sus datos separados por `user_id`.
- **IA segura:** System prompts fijos anti-prompt-injection; los agentes nunca revelan código, claves o arquitectura interna.
- **Túnel:** Cloudflare Tunnel con TLS 1.3, sin puertos abiertos.

---

## 🧪 APIs de Agentes (Prototipo)

Una vez autenticado, puedes probar los agentes:

```bash
# Chat con agentes especializados
curl -X POST http://localhost:8000/api/agents/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿qué gastos puedo deducir?"}'

# Procesar ticket con agentes
curl -X POST http://localhost:8000/api/agents/process-ticket \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "<base64>"}'
```

---

## 👨‍💻 Desarrollo

```bash
# Tests
cd backend && python -m pytest tests/

# Lint
cd backend && flake8 app/ --max-line-length=100 --extend-ignore=E203,W503

# Build frontend
cd frontend && npm run build
```

---

## 📄 Licencia

Este es un proyecto privado. Todos los derechos reservados.

---

<p align="center">Hecho con ❤️ en México</p>
