# 🏦 Sistema Financiero

Sistema automatizado de gestión de tickets, facturas (CFDI) y finanzas personales. Procesa fotos de tickets recibidos por WhatsApp/Telegram, extrae datos con OCR, solicita facturas automáticamente en portales web, organiza todo en Google Drive, y genera análisis financieros con dashboards interactivos.

---

## 🚀 Funcionalidades Principales

### 📸 Captura Inteligente de Tickets
- Recibe fotos de tickets por **WhatsApp** y **Telegram**
- **OCR con Gemini Vision AI** - extrae tienda, fecha, productos, precios
- Soporte para tickets en **español e inglés**
- Procesamiento de imágenes (enderezado, contraste, eliminación de fondo)

### 🤖 Facturación Automática (CFDI)
- Navega automáticamente los portales de facturación de:
  - 🏬 Liverpool, IKEA, Walmart, Amazon, Home Depot
  - 🏪 Oxxo, Farmacias Similares, Costco, Sam's Club
  - ⛽ Pemex, BP y más
- **Accede con credenciales guardadas** (cifradas con AES-256-GCM)
- Si **no hay cuenta registrada**, el bot la crea automáticamente y guarda las credenciales
- Busca facturas en **Gmail** si no están disponibles en el portal
- **Deduplicación** por hash SHA-256 (evita archivos duplicados)

### 📁 Organización Inteligente en Google Drive
```
📁 Drive Principal/
├── 📁 FACTURAS/
│   ├── 📁 Por Establecimiento/Liverpool/2026/
│   ├── 📁 Por Tipo de Gasto/Hogar/
│   ├── 📁 GARANTÍAS/              ← Detecta productos con garantía
│   ├── 📁 Tickets Vencidos/       ← Plazo de facturación expirado
│   ├── 📁 Errores/               ← OCR fallido o error de scraping
│   └── 📁 Credenciales/          ← Contraseñas generadas
```

### 📊 Dashboard Financiero
- **Gastos por categoría** (alimentos, hogar, electrónicos, etc.)
- **Detección de fugas de dinero**: "Estás gastando $25/día en café = $750/mes. Comprando el paquete de $180 ahorras $570/mes"
- **Ahorro semanal sugerido** para compras planeadas
- **Predicción de gastos** con machine learning (Prophet)
- **Alertas de presupuesto** cuando se excede una categoría

### 🛒 Lista de Compras Inteligente
- **Detección automática de ciclos de consumo**: ¿Cada cuánto compras papel higiénico, leche, arroz?
- **Generación automática** de lista basada en patrones de consumo
- **Flujo de aprobación familiar**:
  1. Sistema genera lista sugerida
  2. → Comparte por WhatsApp/Telegram a la familia
  3. → Cada miembro vota (aprueba/rechaza/sugiere)
  4. → Jefe familiar autoriza cambios
  5. → Lista final aprobada
- **Botón "Pre-ordenar en línea"** (links directos)
- **Impresión en impresora térmica** (57mm o 80mm, USB/Bluetooth)
- **Actualización en tiempo real**: cuando llega un ticket nuevo, marca productos comprados

### 🔐 Gestión de Credenciales
- Cifrado **AES-256-GCM** para contraseñas de portales
- Generación automática de contraseñas seguras
- Compatible con **Apple Keychain** y **Google Password Manager**
- Rotación de credenciales

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|---|---|
| **Backend** | Python 3.12 + FastAPI |
| **Base de Datos** | PostgreSQL 16 (async) |
| **OCR** | Gemini Vision AI API |
| **Web Scraping** | Playwright (headless Chromium) |
| **Bots** | python-telegram-bot + Twilio (WhatsApp) |
| **Email** | Gmail API (OAuth2) |
| **Almacenamiento** | Google Drive API + iCloud (opcional) |
| **Dashboard** | Next.js 15 + Recharts + Tailwind CSS 4 |
| **Tareas Asíncronas** | Celery + Redis |
| **Impresión Térmica** | python-escpos (USB) / bleak (Bluetooth) |
| **Cifrado** | cryptography (AES-256-GCM) |
| **Contenedores** | Docker + docker-compose |
| **CI/CD** | GitHub Actions → Hostinger VPS |

---

## 📋 Prerequisitos

- **Python 3.12+** (local o Docker)
- **Node.js 22+** (para frontend)
- **PostgreSQL 16** (o Docker)
- **Redis 7** (para Celery, o Docker)
- **Docker Desktop** (recomendado para desarrollo)
- **Gemini API Key** (gratuita en Google AI Studio)
- **Google Cloud Project** (para Gmail + Drive APIs)
- **Cuenta de Telegram** (para el bot)

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd Sistema\ financiero
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus claves y tokens
nano .env
```

Variables requeridas:
- `GEMINI_API_KEY` - Tu clave de Gemini AI
- `TELEGRAM_BOT_TOKEN` - Token de BotFather
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` - Para Gmail + Drive
- `SECRET_KEY` - Clave maestra para cifrado (cambiar en producción)

### 3. Iniciar con Docker (recomendado)

```bash
docker-compose up -d
```

Esto inicia:
- PostgreSQL en `localhost:5432`
- Redis en `localhost:6379`
- Backend API en `localhost:8000`
- Frontend en `localhost:3000`
- Celery Worker + Beat en background

### 4. Instalación local (alternativa)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # En macOS/Linux
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload

# Frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

### 5. Configurar el Bot de Telegram

1. Habla con [@BotFather](https://t.me/BotFather) en Telegram
2. Crea un nuevo bot: `/newbot`
3. Copia el token en `TELEGRAM_BOT_TOKEN` en `.env`
4. Configura webhook o usa polling (automático en desarrollo)

### 6. Configurar Google APIs

1. Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com)
2. Habilita **Gmail API** y **Google Drive API**
3. Crea credenciales OAuth 2.0 (Desktop App)
4. Descarga el JSON y extrae `client_id`, `client_secret`
5. Genera refresh token (ver `scripts/generate_google_tokens.py`)

---

## 🏗️ Estructura del Proyecto

```
Sistema financiero/
├── backend/                          # Python FastAPI
│   ├── app/
│   │   ├── main.py                   # Entry point
│   │   ├── config.py                 # Configuración
│   │   ├── celery_app.py             # Tareas asíncronas
│   │   ├── database/
│   │   │   ├── connection.py         # Conexión PostgreSQL
│   │   │   └── models.py             # Modelos SQLAlchemy
│   │   ├── modules/
│   │   │   ├── ocr/                  # OCR con Gemini Vision
│   │   │   ├── bots/                 # Telegram + WhatsApp
│   │   │   ├── facturacion/
│   │   │   │   ├── portales/         # Drivers por tienda
│   │   │   │   └── email/            # Búsqueda en Gmail
│   │   │   ├── almacenamiento/       # Google Drive / iCloud
│   │   │   ├── clasificacion/        # Categorización
│   │   │   ├── garantias/            # Detección de garantías
│   │   │   ├── finanzas/             # Análisis financiero
│   │   │   └── shopping_list/        # Lista de compras
│   │   └── utils/
│   │       ├── crypto.py             # Cifrado AES-256
│   │       ├── hashing.py            # SHA-256 deduplicación
│   │       └── validators.py         # Validaciones
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                         # Next.js Dashboard
│   ├── app/
│   │   ├── dashboard/                # Reportes financieros
│   │   ├── shopping-list/            # Lista de compras
│   │   └── settings/                 # Configuración
│   └── package.json
├── hardware/                         # Impresora térmica
├── scripts/                          # Utilidades
├── docs/                             # Documentación
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🤖 Uso del Bot

### Comandos de Telegram

| Comando | Descripción |
|---|---|
| `/start` | Inicia la conversación |
| `/status` | Estado del último ticket |
| `/facturas` | Resumen de facturación |
| `/dashboard` | Link al dashboard |
| `/lista` | Generar lista de compras |
| `/resumen` | Resumen financiero del mes |
| `/ayuda` | Ayuda y comandos |

### Flujo de uso

```
1. 📸 Toma foto del ticket
2. 📤 Envía por Telegram o WhatsApp
3. 🤖 Bot responde:
   "✅ Ticket identificado: Liverpool - $2,350 - 15/06/2026
    🔍 Procesando factura..."
4. ✅ Factura solicitada y guardada en Drive
5. 📊 Análisis financiero actualizado
```

---

## 🧪 Desarrollo

### Pruebas

```bash
cd backend
pytest tests/ -v
```

### Migraciones de Base de Datos

```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "descripcion"
alembic upgrade head
```

### Nuevos Portales de Facturación

1. Crear archivo en `backend/app/modules/facturacion/portales/`
2. Heredar de `BasePortal` (ver `portales/base.py`)
3. Implementar métodos: `login()`, `request_invoice()`, `download_files()`
4. Registrar en `portales/__init__.py`

---

## 📦 Producción

### Deploy en Hostinger VPS

```bash
# 1. Conectar al servidor
ssh usuario@tu-servidor.com

# 2. Clonar repositorio
git clone <repo-url> /opt/sistema-financiero
cd /opt/sistema-financiero

# 3. Configurar variables de entorno
cp .env.example .env
nano .env

# 4. Iniciar con Docker
docker-compose -f docker-compose.yml up -d

# 5. Configurar Nginx reverse proxy
# (ver docs/nginx.conf)
```

### GitHub Actions (CI/CD)

El workflow automatizado:
1. Push a `main` → tests → build Docker images
2. Deploy automático a Hostinger
3. Notificaciones de estado

---

## 📄 Licencia

MIT

---

## 🙌 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork del proyecto
2. Crea tu rama (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add: nueva funcionalidad'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request