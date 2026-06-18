# 🏗️ Sistema Financiero — Arquitectura Completa (Fases 0-3 + Infraestructura)

## 📋 Índice
1. [Visión General](#1-visión-general)
2. [Stack Tecnológico Completo](#2-stack-tecnológico-completo)
3. [Arquitectura del Sistema](#3-arquitectura-del-sistema)
4. [Flujo de Datos Completo](#4-flujo-de-datos-completo)
5. [Base de Datos (PostgreSQL)](#5-base-de-datos-postgresql)
6. [Módulo OCR y Procesamiento de Imágenes](#6-módulo-ocr-y-procesamiento-de-imágenes)
7. [Módulo de Clasificación](#7-módulo-de-clasificación)
8. [Módulo de Facturación Automática](#8-módulo-de-facturación-automática)
9. [Módulo de Almacenamiento en Google Drive](#9-módulo-de-almacenamiento-en-google-drive)
10. [Módulo de Búsqueda en Gmail](#10-módulo-de-búsqueda-en-gmail)
11. [Módulo de Análisis Financiero](#11-módulo-de-análisis-financiero)
12. [Módulo de Lista de Compras Inteligente](#12-módulo-de-lista-de-compras-inteligente)
13. [Módulo de Garantías](#13-módulo-de-garantías)
14. [Bot de Telegram](#14-bot-de-telegram)
15. [Frontend Dashboard](#15-frontend-dashboard)
16. [Seguridad y Cifrado](#16-seguridad-y-cifrado)
17. [Tareas Programadas (Celery)](#17-tareas-programadas-celery)
18. [Infraestructura y CI/CD](#18-infraestructura-y-cicd)

---

## 1. Visión General

**Sistema Financiero** es una plataforma automatizada que:

1. **Recibe fotos de tickets** por Telegram/WhatsApp
2. **Extrae datos** con OCR (Gemini Vision AI)
3. **Solicita facturas** automáticamente en portales web (9 tiendas)
4. **Organiza** PDFs y XMLs en Google Drive
5. **Analiza** gastos y detecta fugas de dinero
6. **Genera** listas de compras inteligentes
7. **Gestiona** garantías de productos
8. **Notifica** al usuario por el bot

---

## 2. Stack Tecnológico Completo

### 2.1 Backend — Python + FastAPI

| Componente | Tecnología | Versión | Propósito |
|-----------|-----------|---------|-----------|
| **Framework** | FastAPI | 0.115.0 | API REST asíncrona |
| **Servidor** | Uvicorn | 0.30.0 | Servidor ASGI de alto rendimiento |
| **Validadción** | Pydantic | 2.9.0 | Schemas y validación de datos |
| **ORM** | SQLAlchemy | 2.0.35 | Base de datos asíncrona |
| **Driver DB** | asyncpg | 0.29.0 | PostgreSQL asíncrono nativo |

### 2.2 Base de Datos — PostgreSQL

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Motor** | PostgreSQL 16 | Base de datos relacional principal |
| **Migraciones** | Alembic | Control de versiones del esquema |
| **Pool de conexiones** | SQLAlchemy pool | 5-10 conexiones simultáneas |

### 2.3 Cache y Colas — Redis + Celery

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Cache** | Redis 7 | Almacenamiento en memoria |
| **Cola de tareas** | Celery 5.4 | Tareas asíncronas en background |
| **Broker** | Redis (via Celery) | Comunicación entre servicios |
| **Tareas programadas** | Celery Beat | 6 tareas automáticas diarias/semanales |

### 2.4 Inteligencia Artificial — Google Gemini

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| **OCR de tickets** | Gemini 2.0 Flash API | Extracción de texto de imágenes |
| **Prompt engineering** | Custom prompt | Optimizado para tickets mexicanos |
| **Límite gratis** | 60 requests/minuto | Sin costo inicial |

### 2.5 Web Scraping — Playwright

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Navegador** | Chromium headless | Automatización de portales web |
| **Framework** | Playwright 1.47 | Control de navegador asíncrono |
| **User Agent** | Chrome 125 (Mac) | Simula navegador real |

### 2.6 Bots — Telegram

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Bot de Telegram** | python-telegram-bot 21 | Interfaz de usuario principal |
| **Manejo de fotos** | filters.PHOTO | Recepción de imágenes de tickets |
| **Comandos** | CommandHandler | /start, /status, /dashboard, etc. |
| **Botones inline** | InlineKeyboardMarkup | Acciones rápidas en respuestas |

### 2.7 APIs de Google

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Gmail** | google-api-python-client | Búsqueda de facturas en email |
| **Google Drive** | google-api-python-client | Almacenamiento de PDFs y XMLs |
| **Autenticación** | OAuth 2.0 + Refresh Token | Acceso sin intervención manual |

### 2.8 Procesamiento de Imágenes

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Manipulación** | Pillow (PIL) | Redimensionar, formato JPEG |
| **Mejora** | ImageEnhance | Contraste + nitidez |
| **Redimensionamiento** | LANCZOS | 2048px máximo para Gemini |

### 2.9 Cifrado y Seguridad

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Cifrado simétrico** | AES-256-GCM | Cifrado de contraseñas de portales |
| **Derivación de llaves** | PBKDF2 (100K iteraciones) | Protección contra fuerza bruta |
| **Hashing** | SHA-256 | Deduplicación de archivos |
| **Tokens JWT** | python-jose | Autenticación de API |

### 2.10 Frontend — Next.js

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Framework** | Next.js 14 | SSR, rutas, React |
| **Gráficos** | Recharts 2.12 | Dashboard financiero interactivo |
| **CSS** | Tailwind CSS 3.4 | Estilos modernos y responsivos |
| **Iconos** | Lucide React | Iconografía del dashboard |

### 2.11 Infraestructura

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Virtualización** | Proxmox VE (LXC) | Contenedores ligeros |
| **Contenedores** | Docker + docker-compose | Microservicios empaquetados |
| **Proxy** | Nginx | Reverse proxy + SSL |
| **SSL** | Let's Encrypt + Certbot | HTTPS gratuito |
| **CI/CD** | GitHub Actions | Automatización de deploys |
| **VPS** | Hostinger VPS | Servidor de producción |

---

## 3. Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USUARIO                                          │
│              📸 Foto del ticket                                         │
└──────────────┬──────────────────────────────────────────────────────────┘
               │ Telegram / WhatsApp
               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    CAPA DE ENTRADA (Bots)                                │
│  ┌───────────────────┐    ┌───────────────────┐                         │
│  │  Telegram Bot      │    │  WhatsApp Bot     │                         │
│  │  (polling/webhook) │    │  (Twilio API)     │                         │
│  └────────┬──────────┘    └────────┬──────────┘                         │
└───────────┼────────────────────────┼─────────────────────────────────────┘
            │                        │
            └──────────┬─────────────┘
                       │ FastAPI endpoint
                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    CAPA DE API (FastAPI)                                 │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ /api/ocr   │  │ /api/bots│  │ /api/    │  │ /api/shopping-list   │  │
│  │            │  │          │  │ finanzas │  │                      │  │
│  └──────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘  │
└─────────┼─────────────┼─────────────┼───────────────────┼───────────────┘
          │             │             │                   │
          ▼             ▼             ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    CAPA DE PROCESAMIENTO                                 │
│                                                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────────┐      │
│  │  OCR Service  │   │ Clasificación│   │  Facturación (Scraping) │      │
│  │  (Gemini AI)  │   │  Productos   │   │  Playwright + 9 portales│      │
│  └──────┬───────┘   └──────┬───────┘   └──────────┬─────────────┘      │
│         │                  │                      │                     │
│         ▼                  ▼                      ▼                     │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────────┐      │
│  │ Preprocess   │   │ Garantías    │   │  Gmail Search (fallback)│      │
│  │ (Pillow)     │   │ (Warranty)   │   │  (Gmail API)           │      │
│  └──────────────┘   └──────────────┘   └────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    CAPA DE ALMACENAMIENTO                                │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │                    Google Drive API                            │      │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │      │
│  │  │ Por          │  │ Por Tipo     │  │ GARANTÍAS/       │   │      │
│  │  │ Establecimiento│ │ de Gasto     │  │                  │   │      │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘   │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │                    PostgreSQL                                    │      │
│  │  10 tablas: tickets, products, invoices, credentials, etc.    │      │
│  └──────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    CAPA DE ANÁLISIS                                      │
│                                                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────────┐      │
│  │  Financiero   │   │ Lista de     │   │  Dashboard             │      │
│  │  (Gastos,     │   │ Compras      │   │  (Next.js + Recharts)  │      │
│  │   fugas,      │   │ (Ciclos,     │   │                        │      │
│  │   predicciones)│   │  aprobación) │   │                        │      │
│  └──────────────┘   └──────────────┘   └────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    CAPA DE INFRAESTRUCTURA                                │
│                                                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────────┐      │
│  │  Docker       │   │  Celery +     │   │  GitHub Actions       │      │
│  │  5 servicios  │   │  Redis (cola) │   │  CI/CD Automático     │      │
│  └──────────────┘   └──────────────┘   └────────────────────────┘      │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Proxmox LXC (Mini PC)          Hostinger VPS                    │   │
│  │  - Staging / Pruebas             - Producción                    │   │
│  │  - DB de prueba                  - SSL / HTTPS                   │   │
│  │  - Snapshots                     - Backup diario DB              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Flujo de Datos Completo

```
FASE 0: SETUP
══════════════════════════════════════════════════════════════════
[No hay flujo de datos aún — solo infraestructura]
- Docker compose con 5 servicios
- PostgreSQL con 14 tablas creadas
- Redis + Celery configurados
- Git inicializado

FASE 1: OCR + BOT + CLASIFICACIÓN
══════════════════════════════════════════════════════════════════
📸 Foto del ticket
       │
       ▼
┌─────────────────────────────┐
│ Pillow (preprocess)         │
│ - Contraste × 1.5          │
│ - Nitidez × 2.0            │
│ - Redimensionar a 2048px   │
└──────────┬──────────────────┘
           │ bytes JPEG
           ▼
┌─────────────────────────────┐
│ Gemini Vision API           │
│ Prompt: "Analiza el ticket  │
│ mexicano y extrae JSON..."  │
└──────────┬──────────────────┘
           │ JSON estructurado
           ▼
┌─────────────────────────────┐
│ Clasificación (Python)      │
│ - Categorizar producto      │
│   (15 categorías, 200 kw)   │
│ - Detectar garantía         │
│ - Detectar tipo de gasto    │
└──────────┬──────────────────┘
           │ TicketData completo
           ▼
┌─────────────────────────────┐
│ Bot Telegram responde:      │
│ "✅ Ticket: Liverpool       │
│  Total: $2,350              │
│  Productos: Cafetera..."    │
└─────────────────────────────┘

FASE 2: FACTURACIÓN + DRIVE + GMAIL
══════════════════════════════════════════════════════════════════
TicketData procesado
       │
       ├── ¿Hay credenciales para esta tienda?
       │   ├── Sí → Usarlas (descifradas con AES-256)
       │   └── No → ¿Crear cuenta nueva?
       │       ├── Sí → Generar password → Llenar formulario
       │       └── No → Preguntar al usuario
       │
       ▼
┌─────────────────────────────┐
│ Playwright (headless)       │
│ 1. Navegar al portal        │
│ 2. Login (si requiere)      │
│ 3. Llenar formulario        │
│    (folio, fecha, total)    │
│ 4. Enviar solicitud         │
│ 5. Esperar descarga         │
└──────────┬──────────────────┘
           │
      ╔════╧════╗
      ║  ¿Éxito? ║
      ╚════╤════╝
           │
     Sí    │    No
     │     │
     │     ▼
     │  ┌─────────────────────┐
     │  │ Gmail API            │
     │  │ Buscar: from:tienda  │
     │  │ subject:factura      │
     │  │ after:fecha          │
     │  │ has:attachment       │
     │  └──────────┬──────────┘
     │             │
     │        ╔════╧════╗
     │        ║  ¿Halló? ║
     │        ╚════╤════╝
     │         Sí  │  No
     │         │   │
     │         │   ▼
     │         │  ┌──────────────┐
     │         │  │ Marcar error │
     │         │  │ Notificar    │
     │         │  └──────────────┘
     │         │
     ▼         ▼
┌─────────────────────────────┐
│ Deduplicación (SHA-256)     │
│ ¿El hash ya existe?         │
├── Sí → Saltar (ya guardado) │
└── No → Continuar            │
        │
        ▼
┌─────────────────────────────┐
│ Google Drive API            │
│                             │
│ Guardar en:                 │
│ 📁 Por Establecimiento/     │
│ 📁 Por Tipo de Gasto/       │
│ 📁 GARANTÍAS/ (si aplica)   │
│                             │
│ También guardar metadatos   │
│ en PostgreSQL               │
└─────────────────────────────┘

FASE 3: ANÁLISIS + LISTA + GARANTÍAS
══════════════════════════════════════════════════════════════════
[PROCESO CONTINUO — Cada vez que llega un ticket nuevo]

1. ANÁLISIS FINANCIERO
   ├── Sumar gastos por categoría
   ├── Detectar fugas de dinero
   │   Ej: "Compras café $25/día = $750/mes
   │        vs paquete de $180 = ahorro $570/mes"
   ├── Calcular meta de ahorro
   │   Ej: "Ahorra $150/semana para tener $2,000 al mes"
   └── Predecir gasto próximo mes

2. LISTA DE COMPRAS
   ├── Detectar ciclo de consumo
   │   Ej: Leche cada 7 días, Arroz cada 15
   ├── Generar lista semanal
   ├── Compartir en familia (votación)
   ├── Aprobación del jefe familiar
   └── Imprimir en térmica (57mm/80mm)

3. GARANTÍAS
   ├── ¿Producto con garantía?
   ├── Calcular fecha de vencimiento
   ├── ¿Vence en <30 días? → Alerta 🔔
   └── Guardar copia en carpeta GARANTÍAS

4. CELERY (Tareas programadas)
   ├── 23:00 → Análisis diario
   ├── Domingo 08:00 → Lista de compras
   ├── Día 1 del mes → Reporte mensual
   └── 06:00 diario → Tickets vencidos
```

---

## 5. Base de Datos (PostgreSQL)

### 5.1 Diagrama de Tablas

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────────┐
│   tickets    │       │    products       │       │    invoices      │
├──────────────┤       ├──────────────────┤       ├──────────────────┤
│ id (PK)      │──1:N──│ id (PK)          │       │ id (PK)          │
│ user_id      │       │ ticket_id (FK)   │       │ ticket_id (FK)   │
│ store_name   │       │ name             │──1:1──│ user_id          │
│ store_cat    │       │ category         │       │ invoice_uuid     │
│ purchase_date│       │ total_price      │       │ pdf_drive_url    │
│ total_amount │       │ has_warranty     │       │ xml_drive_url    │
│ status       │       │ is_consumable    │       │ pdf_hash         │
│ ocr_raw_text │       │ is_high_value    │       │ source           │
│ has_warranty │       │ consumption_cycle│       │ email_message_id │
└──────────────┘       └──────────────────┘       └──────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ store_credentials│    │ consumption_cycles│    │  shopping_lists  │
├──────────────────┤    ├──────────────────┤    ├──────────────────┤
│ id (PK)          │    │ id (PK)          │    │ id (PK)          │
│ user_id          │    │ user_id          │    │ user_id          │
│ store_name       │    │ product_name     │    │ title            │
│ store_category   │    │ avg_days_between │    │ status           │
│ encrypted_user   │    │ last_purchase    │    │ estimated_total  │
│ encrypted_pass   │    │ next_estimated   │    │ approved_budget  │
│ has_account      │    │ preferred_store  │    │ printed          │
│ rfc              │    │ auto_generate    │    └────────┬─────────┘
└──────────────────┘    └──────────────────┘             │
                                                          │ 1:N
                    ┌──────────────────┐    ┌─────────────┴──────────┐
                    │  family_votes    │    │    shopping_items       │
                    ├──────────────────┤    ├────────────────────────┤
                    │ id (PK)          │    │ id (PK)                │
                    │ shopping_list_id │    │ shopping_list_id (FK)  │
                    │ member_name      │    │ product_name           │
                    │ member_role      │    │ quantity               │
                    │ approved         │    │ estimated_price        │
                    │ suggested_item   │    │ preferred_store        │
                    └──────────────────┘    │ status                 │
                                            │ matched_ticket_id      │
                    ┌──────────────────┐    └────────────────────────┘
                    │ financial_analysis│
                    ├──────────────────┤
                    │ id (PK)          │
                    │ user_id          │
                    │ total_spent      │
                    │ category_spending│ (JSON)
                    │ detected_leaks   │ (JSON)
                    │ savings_suggest  │ (JSON)
                    │ predictions      │ (JSON)
                    │ summary_text     │
                    └──────────────────┘
```

### 5.2 Descripción de Tablas

| Tabla | Registros típicos | Tamaño estimado | Propósito |
|-------|------------------|-----------------|-----------|
| `tickets` | 100-500/mes | ~50KB c/u | Datos OCR de cada ticket |
| `products` | 5-20/ticket | ~2KB c/u | Productos individuales |
| `invoices` | 1/ticket | ~1KB | Metadatos de facturas |
| `store_credentials` | 10-20 fijas | ~500B | Credenciales cifradas |
| `consumption_cycles` | 50-200 | ~200B | Ciclos de consumo detectados |
| `shopping_lists` | 4-8/mes | ~5KB | Listas de compras generadas |
| `shopping_items` | 10-30/lista | ~500B | Items de cada lista |
| `family_votes` | 2-5/lista | ~200B | Votaciones familiares |
| `financial_analysis` | 1/día | ~10KB | Análisis financiero cacheado |
| `audit_logs` | 50-100/día | ~500B | Registro de acciones |

---

## 6. Módulo OCR y Procesamiento de Imágenes

### Tecnología
- **Google Gemini 2.0 Flash API** — OCR principal
- **Pillow (PIL)** — Preprocesamiento de imágenes
- **Custom Prompt Engineering** — Optimizado para tickets mexicanos

### Arquitectura
```
┌──────────────────────────────────────────────────────────────┐
│  OCRService (service.py)                                      │
│                                                               │
│  ┌─────────────────┐                                         │
│  │ preprocess_image │ → Contraste × 1.5                      │
│  │                  │ → Nitidez × 2.0                        │
│  │                  │ → Redimensionar a ≤2048px              │
│  │                  │ → RGB → JPEG quality 95                │
│  └────────┬─────────┘                                         │
│           │ bytes                                              │
│           ▼                                                    │
│  ┌─────────────────┐                                         │
│  │ extract_from_img │ → Llamar Gemini con prompt             │
│  │                  │ → Parsear JSON response                │
│  │                  │ → Validar fechas (formatos MX)         │
│  │                  │ → Clasificar tipo de gasto             │
│  │                  │ → Devolver OCRTicketData               │
│  └─────────────────┘                                         │
└──────────────────────────────────────────────────────────────┘
```

### Prompt de Gemini (traducido)
```
"Eres un experto en tickets mexicanos. Extrae:
- store_name, store_category
- receipt_number, purchase_date, purchase_time
- subtotal, taxes, total_amount, payment_method
- products: [{name, brand, quantity, unit, unit_price, total_price, category}]
- has_warranty_items (true si hay electrónicos/muebles/herramientas)
Responde SOLO con JSON, sin markdown."
```

### Formato de salida
```json
{
  "store_name": "Liverpool",
  "store_category": "liverpool",
  "purchase_date": "2026-06-15",
  "total_amount": 2350.00,
  "products": [
    {"name": "Cafetera", "category": "electronicos", "total_price": 1299},
    {"name": "Camisa", "category": "ropa", "total_price": 851}
  ],
  "has_warranty_items": true
}
```

### API Endpoints
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/ocr/process-image` | Subir imagen de ticket |
| `POST` | `/api/ocr/process-base64` | Enviar imagen en base64 |
| `POST` | `/api/ocr/preprocess` | Preprocesar imagen (mejorar calidad) |

---

## 7. Módulo de Clasificación

### Tecnología
- **Python puro** (sin AI) — Lógica basada en reglas y keywords
- **200+ palabras clave** en 15 categorías

### Categorías de Productos
| Categoría | Ejemplos | Keywords |
|-----------|----------|----------|
| `alimentos` | Leche, pan, huevo, arroz | 40 keywords |
| `bebidas` | Agua, refresco, cerveza | 18 keywords |
| `hogar` | Jabón, shampoo, detergente | 28 keywords |
| `electronicos` | TV, laptop, cafetera | 38 keywords |
| `muebles` | Colchón, sofá, mesa | 18 keywords |
| `ropa` | Camisa, pantalón, zapatos | 22 keywords |
| `salud` | Medicina, vitaminas | 14 keywords |
| `higiene` | Pasta dental, papel | 22 keywords |
| `limpieza` | Cloro, fabuloso | 20 keywords |
| `herramientas` | Taladro, martillo | 16 keywords |
| `automotriz` | Llanta, aceite | 14 keywords |
| `combustible` | Gasolina, diesel | 6 keywords |
| `entretenimiento` | Libro, juguete | 10 keywords |

### Reglas de Clasificación
```
¿Producto tiene garantía?
  ├── electrónicos > $500 → Sí (12-36 meses)
  ├── muebles > $1,000 → Sí (24-60 meses)
  ├── herramientas > $500 → Sí (12-24 meses)
  └── otro → No

¿Producto es consumible?
  ├── alimentos, bebidas → Sí (perecedero)
  ├── higiene, limpieza → Sí
  └── electrónicos, muebles → No (duradero)

¿Ciclo de consumo estimado?
  ├── leche, pan, huevo → 7 días
  ├── arroz, pasta, aceite → 15 días
  ├── detergente, jabón → 30 días
  └── otro → No definido
```

---

## 8. Módulo de Facturación Automática

### Tecnología
- **Playwright** (headless Chromium) — Automatización de navegador
- **Patrón de diseño:** Template Method (clase base abstracta)
- **Portal Factory** — Registro dinámico de portales

### Arquitectura
```
┌──────────────────────────────────────────────────────────────┐
│  BasePortal (base.py) — Abstract class                       │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  async run(credentials, ticket_data) → InvoiceResult    │  │
│  │                                                         │  │
│  │  1. Lanzar Chromium headless                           │  │
│  │  2. Crear contexto (viewport, UA, locale)              │  │
│  │  3. login(page, credentials)          ← abstract       │  │
│  │  4. request_invoice(page, data)       ← abstract       │  │
│  │  5. download_files(page)              ← abstract       │  │
│  │  6. Cerrar navegador                                   │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
               ▲              ▲              ▲
               │              │              │
    ┌──────────┴──┐  ┌────────┴────────┐  ┌─┴──────────────┐
    │ Liverpool   │  │ Walmart        │  │ IKEA           │
    │ login: email │  │ login: email   │  │ login: no req  │
    │ + pass      │  │ + pass         │  │                │
    └─────────────┘  └────────────────┘  └────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  PortalFactory (__init__.py)                                  │
│                                                               │
│  _portals = {                                                 │
│      "liverpool": LiverpoolPortal,           ← registrado    │
│      "ikea": IKEAPortal,                     ← registrado    │
│      "walmart": WalmartPortal,               ← registrado    │
│      "amazon": AmazonPortal,                 ← registrado    │
│      "home_depot": HomeDepotPortal,          ← registrado    │
│      "oxxo": OxxoPortal,                     ← registrado    │
│      "farmacias_similares": FarmaciasSimilaresPortal, ← reg  │
│      "pemex": PemexPortal,                   ← registrado    │
│      "bp": BPPortal,                         ← registrado    │
│  }                                                             │
│                                                               │
│  create("liverpool") → LiverpoolPortal()                     │
│  get_supported_stores() → ["liverpool", "ikea", ...]          │
└──────────────────────────────────────────────────────────────┘
```

### Portal de Liverpool (ejemplo detallado)
```
1. Navegar a https://www.liverpool.com.mx/facturacion
2. Hacer clic en "Iniciar sesión"
3. Llenar email → credentials.username
4. Llenar password → credentials.password
5. Hacer clic en "Entrar"
6. Esperar navegación (verificar que no haya error)
7. Llenar folio del ticket → ticket_data.receipt_number
8. Llenar fecha de compra → ticket_data.purchase_date
9. Llenar total → ticket_data.total_amount
10. Hacer clic en "Solicitar factura"
11. Esperar resultado
12. Buscar enlaces de descarga PDF y XML
13. Descargar ambos archivos
14. Cerrar navegador
```

### Portal IKEA (sin login)
```
1. Navegar a https://www.ikea.com/mx/es/customer-service/facturacion/
2. Llenar número de orden
3. Llenar fecha de compra
4. Llenar total
5. Llenar RFC
6. Hacer clic en "Solicitar"
7. Descargar PDF + XML
```

---

## 9. Módulo de Almacenamiento en Google Drive

### Tecnología
- **Google Drive API v3** — Operaciones de archivos y carpetas
- **OAuth 2.0** — Autenticación con refresh token
- **MediaIoBaseUpload** — Subida en memoria (sin archivos temporales)

### Estructura de Carpetas (Auto-creada)
```
📁 FACTURAS/                           ← Carpeta raíz
│
├── 📁 Por Establecimiento/
│   ├── 📁 Liverpool/
│   │   ├── 📁 2026/
│   │   │   ├── Liverpool_20260615_abc123.pdf   ← Factura PDF
│   │   │   └── Liverpool_20260615_abc123.xml   ← CFDI XML
│   │   └── 📁 2027/
│   ├── 📁 IKEA/
│   ├── 📁 Walmart/
│   ├── 📁 Amazon/
│   ├── 📁 Home Depot/
│   ├── 📁 Oxxo/
│   ├── 📁 Farmacias Similares/
│   ├── 📁 Pemex/
│   └── 📁 BP/
│
├── 📁 Por Tipo de Gasto/
│   ├── 📁 Alimentos y Bebidas/
│   ├── 📁 Hogar/
│   ├── 📁 Electrónicos/
│   ├── 📁 Muebles/
│   ├── 📁 Ropa y Accesorios/
│   ├── 📁 Salud y Farmacia/
│   ├── 📁 Higiene/
│   ├── 📁 Limpieza/
│   ├── 📁 Herramientas/
│   ├── 📁 Automotriz/
│   ├── 📁 Combustible/
│   ├── 📁 Entretenimiento/
│   └── 📁 Otros Gastos/
│
├── 📁 GARANTÍAS/                        ← Productos con garantía
│   ├── Liverpool_20260615_Cafetera_GARANTIA.pdf
│   └── IKEA_20260615_Colchon_GARANTIA.pdf
│
├── 📁 Tickets Vencidos/                ← Plazo > 60 días
│
├── 📁 Errores/                         ← OCR/scraping fallido
│
└── 📁 Credenciales/                     ← Contraseñas generadas
    └── Credenciales_Liverpool_20260615.txt
```

### Flujo de Guardado
```
save_invoice(store_name, purchase_date, pdf_bytes, xml_bytes, ticket_id, ...)
  │
  ├── 1. Asegurar estructura de carpetas
  │     (crear si no existen)
  │
  ├── 2. Guardar en 📁 Por Establecimiento/Tienda/Año/
  │     → PDF + XML
  │
  ├── 3. Guardar en 📁 Por Tipo de Gasto/Categoría/Año/
  │     → PDF (copia organizada)
  │
  ├── 4. Si has_warranty → 📁 GARANTÍAS/
  │     → PDF (copia con sufijo _GARANTIA)
  │
  └── 5. Guardar metadatos en PostgreSQL
        (urls, file_ids, hashes SHA-256)
```

---

## 10. Módulo de Búsqueda en Gmail

### Tecnología
- **Gmail API v1** — Búsqueda y descarga de correos
- **OAuth 2.0** — Refresh token para acceso continuo
- **asyncio.to_thread** — API síncrona envuelta en async

### Estrategia de Búsqueda
```
search_invoice(store_name, purchase_date, total_amount, ticket_number)
  │
  ├── Construir query Gmail:
  │     from:(liverpool.com.mx OR facturacion@liverpool.com.mx)
  │     subject:(factura OR cfdi OR invoice)
  │     after:2026/06/01 before:2026/07/01
  │     has:attachment
  │     (T123456)              ← número de ticket
  │     (2350)                 ← monto total
  │
  ├── Buscar mensajes (max 5 resultados)
  │
  ├── Por cada mensaje:
  │   ├── Extraer headers (Subject, From, Date)
  │   ├── Aplanar partes del mensaje (multipart)
  │   ├── Buscar attachments .pdf y .xml
  │   └── Descargar usando attachmentId
  │
  └── Devolver EmailInvoiceResult
      { found: true, pdf_bytes: ..., xml_bytes: ... }
```

### Patrones de Email por Tienda
| Tienda | Email patterns |
|--------|---------------|
| Liverpool | `liverpool.com.mx`, `facturacion@liverpool.com.mx` |
| IKEA | `ikea.com`, `ikea.com.mx` |
| Walmart | `walmart.com`, `walmart.com.mx` |
| Amazon | `amazon.com.mx`, `shipment-tracking@amazon.com.mx` |
| Home Depot | `homedepot.com.mx` |
| Oxxo | `oxxo.com` |
| Pemex | `pemex.com` |
| Costco | `costco.com.mx` |
| Soriana | `soriana.com`, `soriana.com.mx` |

---

## 11. Módulo de Análisis Financiero

### Tecnología
- **Python puro** — Cálculos estadísticos simples
- **Dataclasses** — Estructuras de datos tipadas
- **Collections.Counter** — Detección de patrones de compra

### Métricas Generadas
```
📊 Reporte Mensual
├── Total gastado: $XX,XXX
├── Por categoría:
│   ├── Alimentos: $X,XXX (XX%)
│   ├── Hogar: $X,XXX (XX%)
│   ├── Electrónicos: $X,XXX (XX%)
│   └── ...
├── Tendencia: ↑ subiendo / ↓ bajando / → estable
│
├── Fugas de dinero detectadas:
│   ├── "Café: compras $25/día = $750/mes
│   │     vs paquete de $180 = ahorro $570/mes"
│   ├── "Papel: compras $45/semana = $180/mes
│   │     vs paquete grande $110 = ahorro $70/mes"
│   └── ...
│
├── Meta de ahorro:
│   ├── Ahorro semanal sugerido: $XXX
│   ├── Ahorro mensual objetivo: $X,XXX
│   └── "Ahorrando $XXX/semana tendrás $X,XXX al mes"
│
└── Predicción próximo mes:
    ├── Estimado: $XX,XXX
    └── Confianza: alta/media/baja (basado en X meses)
```

### Detección de Fugas (algoritmo)
```
detect_leaks(products)
  │
  ├── 1. Agrupar productos por nombre
  ├── 2. Contar frecuencia de compra
  ├── 3. Si frecuencia ≥ 4 y precio promedio < $50:
  │     └→ Posible fuga detectada
  │        Cálculo: costo_actual vs costo_optimizado (mayoreo -40%)
  │        ahorro_mensual = costo_actual * 0.4
  │        ahorro_anual = ahorro_mensual * 12
  └── 4. Generar recomendación texto
```

---

## 12. Módulo de Lista de Compras Inteligente

### Tecnología
- **Python puro** — Lógica de ciclos y generación de listas
- **Dataclasses** — ShoppingItem, GeneratedList

### Ciclos de Consumo por Defecto
| Producto | Ciclo | Precio estimado |
|----------|-------|----------------|
| Leche | cada 7 días | $28 |
| Pan | cada 7 días | $18 |
| Huevo | cada 7 días | $35 |
| Frutas/Verduras | cada 7 días | $100 |
| Carne/Pollo | cada 7 días | $150 |
| Arroz | cada 15 días | $45 |
| Frijol | cada 15 días | $35 |
| Aceite | cada 15 días | $28 |
| Papel Higiénico | cada 30 días | $85 |
| Detergente | cada 30 días | $65 |
| Jabón | cada 30 días | $18 |
| Pasta dental | cada 30 días | $35 |

### Flujo de Aprobación Familiar
```
1. Sistema genera lista sugerida automáticamente
   (basado en ciclos de consumo)
          │
2. Bot comparte en Telegram/WhatsApp a la familia:
   "🛒 Lista de compras sugerida"
          │
3. Cada miembro puede:
   ✅ Aprobar item
   ❌ Rechazar item
   ➕ Agregar item (nombre + tienda + link)
          │
4. Jefe familiar recibe resumen:
   - Items aprobados
   - Items rechazados
   - Items sugeridos
          │
5. Jefe familiar aprueba o rechaza cambios
          │
6. Lista final → Botón "Pre-ordenar" / "Imprimir"
```

### Formato para Impresora Térmica
```
══════════════════════════════════╗
║        LISTA DE COMPRAS        ║
║     18/06/2026 14:30           ║
╠════════════════════════════════╣
║ 🏪 Walmart                     ║
║ ───────────────────────────── ║
║ 1. Leche x2 lt $28            ║
║ 2. Pan 1 pza $18              ║
║ 3. Huevo 12 pza $35           ║
║ 4. Frutas y Verduras $100     ║
║─────────────────────────────  ║
║ 🏪 Costco                      ║
║ ───────────────────────────── ║
║ 5. Papel Higiénico 12 pza $85 ║
║ 6. Detergente 1 pza $65       ║
╠════════════════════════════════╣
║ TOTAL ESTIMADO: $531.00       ║
║                                ║
║ [ ] Comprado  [ ] Pendiente   ║
║ Impreso: 18/06/2026 14:30     ║
╚════════════════════════════════╝
```

---

## 13. Módulo de Garantías

### Tecnología
- **Python puro** — Cálculo de fechas y reglas de garantía
- **Dataclasses** — WarrantyStatus

### Reglas de Garantía por Categoría
| Categoría | Precio mínimo | Garantía estándar | Garantía extendida |
|-----------|---------------|-------------------|-------------------|
| Electrónicos | $500 | 12 meses (<$5,000) | 36 meses (≥$5,000) |
| Muebles | $1,000 | 24 meses (<$10,000) | 60 meses (≥$10,000) |
| Herramientas | $500 | 12 meses (<$3,000) | 24 meses (≥$3,000) |
| Automotriz | $500 | 36 meses | — |

### Estados de Garantía
```
get_warranty_status(purchase_date, category, price)
  │
  ├── ¿Es garantizable?
  │   ├── No → { has_warranty: false }
  │   └── Sí → Calcular fecha fin
  │
  ├── ¿Días restantes?
  │   ├── < 0 → "expired" (sin alerta)
  │   ├── ≤ 30 → "expiring_soon" ⚠️
  │   │     "¡Tu garantía vence en X días! Revisa antes de que expire"
  │   ├── ≤ 90 → "active" ℹ️
  │   │     "Tu garantía vence en X días"
  │   └── > 90 → "active" (sin alerta)
  │
  └── Devolver { has_warranty, end_date, days_remaining, status, alert }
```

---

## 14. Bot de Telegram

### Tecnología
- **python-telegram-bot 21.0** — Framework de bot
- **Polling mode** — Para desarrollo (sin webhook)
- **Filtros**: CommandHandler, MessageHandler(filters.PHOTO), CallbackQueryHandler

### Comandos
| Comando | Acción |
|---------|--------|
| `/start` | Mensaje de bienvenida + instrucciones |
| `/ayuda` | Lista de comandos y ayuda |
| `/status` | Estado del último ticket procesado |
| `/dashboard` | Link al dashboard web 📊 |
| `/lista` | Generar lista de compras 🛒 |
| `/resumen` | Resumen financiero del mes 📈 |

### Flujo de Conversación
```
Usuario: [Envía foto del ticket]

Bot: "📸 Recibiendo ticket...
      ⏳ Procesando OCR..."

Bot: "✅ Ticket Identificado
      🏪 Tienda: Liverpool
      📅 Fecha: 15/06/2026
      🔢 Total: $2,350.00
      
      📦 Productos:
      1. Cafetera x1 = $1,299.00
      2. Camisa x1 = $851.00
      
      🔧 ¡Producto con garantía detectado!
      
      ⏳ Iniciando facturación...
      Te notificaré cuando esté lista.
      
      [📊 Ver Dashboard] [❌ Reportar Error]"
```

---

## 15. Frontend Dashboard

### Tecnología
- **Next.js 14** — Server-side rendering
- **Recharts 2.12** — Gráficos interactivos (React)
- **Tailwind CSS 3.4** — Estilos utilitarios
- **Lucide React** — Iconos

### Páginas
| Ruta | Contenido |
|------|-----------|
| `/` | Página principal con tarjetas de acceso |
| `/dashboard` | Dashboard financiero completo 📊 |
| `/shopping-list` | Lista de compras interactiva 🛒 |
| `/settings` | Configuración del sistema ⚙️ |

### Componentes del Dashboard (planeados)
```
📊 Dashboard Financiero
├── 📈 Gráfico de Gastos por Categoría (PieChart)
│   ├── Alimentos: 35%
│   ├── Hogar: 20%
│   ├── Electrónicos: 15%
│   └── ...
│
├── 📉 Gráfico de Tendencia Mensual (LineChart)
│   ├── Enero: $12,000
│   ├── Febrero: $11,500
│   ├── Marzo: $13,200
│   └── ...
│
├── 💰 Tarjetas de Resumen
│   ├── Gasto Total: $XX,XXX
│   ├── Ahorro Meta: $X,XXX/mes
│   ├── Fugas Detectadas: X
│   └── Facturas: X/XX
│
├── ⚠️ Alertas de Fugas
│   ├── "Café: $750/mes → $180 ahorro" 🔴
│   └── "Papel: $180/mes → $70 ahorro" 🟡
│
└── 📋 Últimos Tickets
    ├── Liverpool - $2,350 - 15/06
    ├── Walmart - $850 - 14/06
    └── Oxxo - $125 - 13/06
```

---

## 16. Seguridad y Cifrado

### Tecnología
- **cryptography** (AES-256-GCM) — Cifrado simétrico autenticado
- **PBKDF2** con 100,000 iteraciones — Derivación de llaves
- **SHA-256** — Hashing para deduplicación

### Flujo de Cifrado
```
┌────────────────────────────────────────────────────────────┐
│  encrypt(plaintext, context)                                │
│                                                             │
│  1. Generar salt aleatorio (16 bytes)                      │
│  2. Derivar key con PBKDF2(master_key, salt, 100K iter)    │
│  3. Generar nonce aleatorio (12 bytes)                     │
│  4. Cifrar con AES-256-GCM(nonce, plaintext, context)      │
│  5. Devolver (ciphertext, nonce, key_id=base64(salt))      │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  decrypt(ciphertext, nonce, key_id, context)               │
│                                                             │
│  1. Decodificar key_id → salt                              │
│  2. Derivar key con PBKDF2(master_key, salt, 100K iter)    │
│  3. Descifrar con AES-256-GCM(nonce, ciphertext, context)  │
│  4. Verificar autenticidad (tag de 16 bytes)               │
│  5. Devolver plaintext                                     │
└────────────────────────────────────────────────────────────┘
```

### Lo que se cifra
| Dato | ¿Cifrado? | Método |
|------|-----------|--------|
| Contraseñas de portales | ✅ Sí | AES-256-GCM en columna `encrypted_password` |
| Usuarios de portales | ✅ Sí | AES-256-GCM en columna `encrypted_username` |
| Credenciales generadas | ✅ Sí | AES-256-GCM en tabla `credentials_generated` |
| Nombres de productos | ❌ No | No sensible |
| Montos de tickets | ❌ No | No sensible |
| Fechas de compra | ❌ No | No sensible |

---

## 17. Tareas Programadas (Celery)

### Tecnología
- **Celery 5.4** — Tareas asíncronas distribuidas
- **Redis 7** — Broker y backend de resultados
- **Celery Beat** — Programador de tareas periódicas

### Schedule
```
Tarea                    Horario              Descripción
────────────────────     ──────────           ──────────────────────────
generate_daily_analysis   23:00 diario        Actualizar dashboard
generate_weekly_list      Domingo 08:00       Generar lista de compras
generate_monthly_report   Día 1, 08:00        Reporte financiero mensual
check_expired_tickets     06:00 diario        Mover tickets vencidos
update_consumption_cycles  02:00 diario        Actualizar ciclos de consumo
check_missing_purchases   20:00 diario        Preguntar compras no registradas
```

### Arquitectura de Tareas
```
┌──────────────────────────────────────────────────────────────┐
│  Celery Worker (4 procesos concurrentes)                      │
│                                                               │
│  Cola: redis://redis:6379/0                                   │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ OCR Task     │  │ Scraping     │  │ Email Search     │   │
│  │ (25 min max) │  │ Task         │  │ Task (5 min max) │   │
│  └──────────────┘  │ (30 min max) │  └──────────────────┘   │
│                    └──────────────┘                          │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Analysis     │  │ Shopping     │  │ Notification    │   │
│  │ Task         │  │ List Task    │  │ Task (rápida)   │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## 18. Infraestructura y CI/CD

### Arquitectura de Despliegue
```
┌─────────────────────────────────────────────────────────────────┐
│                        GITHUB (main)                            │
│   git push → GitHub Actions → Tests → Build → Deploy            │
└──────────┬────────────────────────────────────┬─────────────────┘
           │                                    │
           ▼                                    ▼
┌──────────────────────┐          ┌──────────────────────────┐
│  🖥️ Mini PC (Local)  │          │  ☁️ Hostinger (Producción)│
│  Proxmox LXC         │          │  VPS Ubuntu              │
│                      │          │                          │
│  CT 100: Docker Host │          │  Docker:                 │
│  ├── PostgreSQL 16   │          │  ├── PostgreSQL 16       │
│  ├── Redis 7         │          │  ├── Redis 7             │
│  ├── Backend         │          │  ├── Backend             │
│  ├── Frontend        │          │  ├── Frontend            │
│  └── Celery Worker   │          │  └── Celery Worker       │
│                      │          │                          │
│  CT 101: DB Test     │          │  Nginx + SSL (Let's Encrypt)
│                      │          │                          │
│  Backup semanal      │          │  Backup DB diario        │
└──────────────────────┘          └──────────────────────────┘
```

### Docker Compose (5 servicios)
```
SERVICIO          IMAGEN                    PUERTOS     DEPENDE DE
────────          ─────                     ───────     ──────────
postgres          postgres:16-alpine        5432        —
redis             redis:7-alpine            6379        —
backend           ./backend/Dockerfile      8000        postgres, redis
celery_worker     ./backend/Dockerfile      —           postgres, redis
celery_beat       ./backend/Dockerfile      —           postgres, redis
frontend          ./frontend/Dockerfile     3000        backend
```

### CI/CD: GitHub Actions (3 workflows)

```
1. CI (ci.yml)
   Trigger: push a develop, feature/*, fix/*
   Jobs:
   ├── test-backend: pytest con PostgreSQL + Redis reales
   ├── lint-backend: flake8 + black
   └── build-docker: build imágenes + validar docker-compose

2. Deploy Staging (deploy-staging.yml)
   Trigger: push a develop
   Jobs:
   └── deploy: SSH a Mini PC → pull → rebuild → health check

3. Deploy Production (deploy-production.yml)
   Trigger: push a main + workflow_dispatch (manual)
   Jobs:
   └── deploy: SSH a Hostinger → backup DB → pull → rebuild → health check
```

### Flujo de Trabajo
```
1. git checkout -b feature/mejora-ocr
2. 👨‍💻 Hacer cambios
3. git push origin feature/mejora-ocr
   → GitHub Actions corre CI (tests + lint)
4. ✅ Aprobar PR a develop
   → GitHub Actions deploya a Mini PC
5. 🧪 Probar en Mini PC con datos de prueba
6. ✅ Aprobar PR a main
   → GitHub Actions backup DB + deploy a Hostinger
7. 🚀 En producción
```

---

## 📊 Resumen de Costos

| Componente | Costo mensual |
|-----------|--------------|
| **Mini PC** (1 vez) | ~$3,000-5,000 MXN |
| **Electricidad** (25W) | ~$50 MXN |
| **Hostinger VPS** | ~$150 MXN |
| **Gemini API** | $0 (60 req/min gratis) |
| **Google APIs** | $0 (cuota gratuita) |
| **GitHub** | $0 |
| **Let's Encrypt SSL** | $0 |
| **Dominio .com** | ~$30 MXN |
| **Total mensual** | **~$230 MXN** |

---

## 🔗 Enlaces Rápidos

| Recurso | URL |
|---------|-----|
| API Docs (dev) | `http://localhost:8000/api/docs` |
| Frontend (dev) | `http://localhost:3000` |
| Health Check | `http://localhost:8000/api/health` |
| GitHub Repo | `https://github.com/TU_USUARIO/sistema-financiero` |
| Dashboard | `http://localhost:3000/dashboard` |