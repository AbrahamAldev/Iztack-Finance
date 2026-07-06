# 🏦 Iztack-Finance

**Iztack** → *Agencia digital y marca tecnológica mexicana especializada en automatización inteligente.*  
**Finance** → *Módulo de gestión financiera personal, familiar y para PyMEs en México.*

> **Tu CFO personal automatizado: de la foto del ticket a la declaración del SAT, sin esfuerzo.**
> Captura tickets por Telegram, factura CFDI en automático, organiza tus gastos, detecta fugas de dinero, arma tu lista de compras inteligente y prepárate para la declaración anual — todo desde un solo lugar.

---

## 📋 Tabla de Contenidos

- [Visión General](#-visión-general)
- [Funcionalidades Completas](#-funcionalidades-completas)
- [Stack Tecnológico](#-stack-tecnológico)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Uso del Bot](#-uso-del-bot)
- [Módulo Fiscal SAT](#-módulo-fiscal-sat)
- [Multi-negocio y POS](#-multi-negocio-y-pos)
- [Almacenamiento y Respaldo](#-almacenamiento-y-respaldo)
- [Despliegue y CI/CD](#-despliegue-y-cicd)
- [Roadmap](#-roadmap)

---

## 🎯 Visión General

Iztack-Finance es un **agente financiero autónomo** que:

1. **Recibe fotos de tickets** por Telegram
2. **Extrae los datos** con OCR (Tesseract local + IA como fallback)
3. **Solicita la factura CFDI** automáticamente en el portal de cada tienda
4. **Organiza todo** en almacenamiento local + nube personal (Google Drive, Dropbox o OneDrive)
5. **Analiza tus gastos** y detecta fugas de dinero
6. **Genera listas de compras inteligentes** que se autoajustan
7. **Prepara tu declaración fiscal** con deducciones aplicables
8. **Gestiona garantías** de productos costosos

---

## 🚀 Funcionalidades Completas

### 📸 Captura Inteligente de Tickets

- Envía una **foto del ticket** desde Telegram
- El agente detecta automáticamente:
  - Tienda o proveedor
  - Fecha y hora de compra
  - Productos, cantidades y precios
  - Subtotal, IVA y total
- **OCR de dos capas:**
  1. **Tesseract 5** (local, gratuito, sin límites) — primera opción
  2. **OpenRouter** (Gemini Flash / Llama 3.2 Vision / Qwen 2-VL) — fallback si confianza < 75%
- Selector de modelo IA configurable desde el dashboard
- Soporte para tickets en español e inglés
- Procesamiento de imágenes (enderezado, contraste, eliminación de fondo)

### 🤖 Facturación Automática (CFDI)

- Navega automáticamente los portales de facturación de **9+ tiendas**:
  - 🏬 Liverpool, IKEA, Walmart, Amazon, Home Depot
  - 🏪 Oxxo, Farmacias Similares, Costco, Sam's Club
  - ⛽ Pemex, BP
- **Accede con credenciales guardadas** (cifradas con AES-256-GCM)
- Si **no hay cuenta registrada**, el bot:
  1. Pregunta si deseas crearla o usar una existente
  2. Si la crea: genera contraseña segura, llena el formulario del portal
  3. Te envía las credenciales en un mensaje que se autodestruye en 60s
  4. Exporta un archivo `.csv` importable a Apple/Google Password Manager
- Busca facturas en **Gmail/Outlook** si no están disponibles en el portal
- **Deduplicación** por hash SHA-256 (evita archivos duplicados)
- Si el plazo de facturación venció (>30 días), marca como "ticket vencido"
- Si el adapter falla 3 veces seguidas, se desactiva automáticamente y notifica

### 📁 Organización Inteligente del Almacenamiento

```
📁 Almacenamiento Local (/data/storage/)
├── 📁 tickets/raw/{YYYY}/{MM}/{sha256}.jpg    ← Fotos originales
├── 📁 tickets/cfdi/{uuid}/                    ← PDFs y XMLs
│   ├── factura.pdf
│   └── factura.xml
├── 📁 reports/{YYYY}-{MM}.pdf                 ← Reportes mensuales
└── 📁 printer-temp/{run-id}.bin               ← Archivos de impresión

📁 Nube Personal (Google Drive / Dropbox / OneDrive) — OPCIONAL
├── 📁 SistemaFinanzas/
│   ├── 📁 Tickets/{YYYY}/{MM}/                ← Fotos organizadas
│   ├── 📁 Facturas/{YYYY}/{MM}/               ← PDFs y XMLs
│   ├── 📁 Garantías/{producto}/               ← Productos con garantía
│   ├── 📁 Tickets Vencidos/                   ← Plazo expirado
│   ├── 📁 Errores/                            ← OCR fallido
│   └── 📁 Credenciales/                       ← Contraseñas exportadas
```

**Si no conectas nube personal:** el sistema te envía un **ZIP mensual por correo** con todos tus archivos y los purga localmente después de 13 meses.

### 📊 Dashboard Financiero

- **Overview** con KPIs: gastos del mes, ticket promedio, facturas pendientes, garantías por vencer
- **Gastos por categoría** (alimentos, hogar, electrónicos, servicios, etc.)
- **Detección de fugas de dinero:**
  - "Estás gastando $25/día en café = $750/mes. Comprando el paquete de $180 ahorras $570/mes"
  - "Compras papel higiénico cada 3 días en vez del paquete de 12 rollos cada 3 semanas"
- **Ahorro semanal sugerido** para compras planeadas
- **Alertas de presupuesto** cuando se excede una categoría
- **Dashboard por negocio** (independiente del familiar)
- **Modo oscuro y modo claro**
- **Diseño minimalista**, responsive (móvil, tablet, desktop)
- **PWA instalable** en el celular

### 🛒 Lista de Compras Inteligente

- **Detección automática de ciclos de consumo:**
  - ¿Cada cuánto compras leche, pan, papel higiénico, arroz?
  - El sistema aprende tus patrones y genera la lista en el momento óptimo
- **Generación automática** de lista basada en patrones de consumo
- **Flujo de aprobación familiar:**
  1. Sistema genera lista sugerida
  2. → Comparte por Telegram a la familia
  3. → Cada miembro vota (aprueba/rechaza/sugiere)
  4. → Si alguien agrega algo: pide nombre, tienda o link directo
  5. → Jefe familiar autoriza o rechaza cambios
  6. → Lista final aprobada
- **Opciones de salida:**
  - **Pre-ordenar en línea** (links directos a Amazon, Walmart, etc.)
  - **Generar link de carrito** para pago manual
  - **Imprimir en impresora térmica** (57mm o 80mm, USB/Bluetooth)
    - Lugar de compra, fecha, cantidades, casillas para palomear
  - **Compartir en Telegram** la lista aprobada
- **Actualización en tiempo real:** cuando llega un ticket nuevo, marca productos comprados y notifica lo que falta

### 🔐 Gestión de Credenciales

- Cifrado **AES-256-GCM** para contraseñas de portales y tokens de nube
- **Dos capas de cifrado:**
  - `APP_ENCRYPTION_KEY` para credenciales CFDI
  - `SENSITIVE_ENCRYPTION_KEY` para datos fiscales (constancia, estados de cuenta)
- Generación automática de contraseñas seguras con `secrets`
- Exportación a **Apple Keychain** y **Google Password Manager** (archivo `.csv`)
- Rotación de credenciales
- Log de accesos con alerta por Telegram en cada uso

### 🛡️ Garantías

- Detecta automáticamente productos con garantía en los tickets:
  - Muebles, colchones (IKEA)
  - Estufas, cafeteras, refrigeradores (Liverpool)
  - Electrónicos, herramientas, etc.
- Calcula `warranty_until = purchase_date + months`
- **Semáforo de estado:** activa, por vencer (30 días), vencida
- Almacena la factura en carpeta especial `/Garantías/{producto}/`
- Notifica por Telegram cuando una garantía está por vencer

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Estado |
|------------|-----------|--------|
| **Backend** | Python 3.12 + FastAPI + SQLAlchemy 2 async | ✅ |
| **Base de Datos** | PostgreSQL 16 (18 tablas, multi-tenant) | ✅ |
| **Cache y Colas** | Redis 7 con AOF | ✅ |
| **Workers** | ARQ (Redis nativo, 3 colas: ocr/cfdi/housekeeping) | ✅ |
| **Scheduler** | ARQ Scheduler (4 tareas periódicas) | ✅ |
| **OCR primario** | Tesseract 5 (local, gratuito) | ⏳ |
| **OCR fallback** | OpenRouter (Gemini Flash / Llama 3.2 Vision) | ⏳ |
| **Web Scraping** | Playwright (headless Chromium) | ✅ |
| **Bot** | python-telegram-bot v21 async | ✅ |
| **Email** | SMTP (Gmail, SendGrid, Mailgun) + IMAP | ✅ |
| **Storage local** | LocalStorage + SensitiveStorage (AES-256-GCM) | ✅ |
| **Storage nube** | Google Drive / Dropbox / OneDrive (OAuth) | ⏳ |
| **Retención** | RetentionManager (purga >13 meses) | ✅ |
| **Email fallback** | EmailStorage (ZIP mensual cifrado) | ✅ |
| **Frontend** | Next.js 15 + Tailwind + shadcn/ui + Recharts | ⏳ |
| **Dashboard** | PWA instalable, modo oscuro/claro | ⏳ |
| **Impresión** | ESC/POS (USB/Bluetooth) + fallback PDF | ⏳ |
| **Cifrado** | cryptography (AES-256-GCM, 2 keys separadas) | ✅ |
| **Proxy** | Caddy (HTTPS automático con Let's Encrypt) | ✅ |
| **Contenedores** | Docker + docker-compose (7 servicios) | ✅ |
| **CI/CD** | GitHub Actions (3 pipelines) | ✅ |

---

## 🏗️ Estructura del Proyecto

```
Iztack-Finance/
├── apps/
│   ├── web/                    Next.js 15 + shadcn/ui
│   ├── bot/                    Telegram Bot (python-telegram-bot v21)
│   ├── api/                    FastAPI (REST + OpenAPI)
│   ├── worker/                 ARQ (7 tareas + scheduler)
│   └── cfdi/portales/          Adapters Playwright (9 portales)
├── packages/
│   ├── shared/                 Modelos SQLAlchemy (18 tablas)
│   ├── storage/                Local + Sensitive + Email + Retention
│   ├── ocr/                    Tesseract + OpenRouter
│   ├── llm/                    Wrapper unificado de IA
│   ├── printer/                ESC/POS + fallback PDF
│   └── analytics/              Ciclos de consumo + fugas
├── infrastructure/
│   ├── docker-compose.yml      Producción (Caddy + 7 servicios)
│   ├── caddy/Caddyfile         HTTPS automático
│   ├── docker/                 Dockerfiles por servicio
│   └── scripts/                Backup, restore, rotación
├── docs/
│   ├── IDEA-ORIGINAL.md        Visión fundacional del proyecto
│   ├── TASK-LIST.md            Estado de avance detallado
│   ├── CHANGELOG.md            Historial de cambios del desarrollo
│   ├── ARQUITECTURA_FINAL_v2.md Stack y servicios actuales
│   ├── GUIA_DEPLOY_PASO_A_PASO.md Tutorial para principiantes
│   ├── HISTORICO_ARQUITECTURA_v1.md Backup de la versión anterior
│   └── INFRAESTRUCTURA.md      Detalles de infraestructura
├── .github/workflows/
│   ├── ci.yml                  Tests + Lint + Build
│   ├── deploy-staging.yml      Deploy a Mini PC (develop)
│   └── deploy-production.yml   Deploy a Hostinger (main)
├── tests/
│   ├── fixtures/tickets/       Fotos de tickets de muestra
│   └── e2e/                    Playwright E2E
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/Iztack-Finance.git
cd Iztack-Finance
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
nano .env
```

Variables requeridas:
| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Clave maestra para cifrado AES-256-GCM |
| `SENSITIVE_ENCRYPTION_KEY` | Clave separada para datos fiscales |
| `TELEGRAM_BOT_TOKEN` | Token de @BotFather |
| `OPENROUTER_API_KEY` | API key de OpenRouter (para fallback OCR) |
| `SMTP_HOST` / `SMTP_USER` / `SMTP_PASSWORD` | Para envío de ZIP mensual |

### 3. Iniciar con Docker

```bash
docker-compose up -d
```

Esto inicia 7 servicios:
| Servicio | Puerto | Propósito |
|----------|--------|-----------|
| Caddy | 443 | Reverse proxy HTTPS |
| PostgreSQL | 5432 | Base de datos |
| Redis | 6379 | Cache + cola ARQ |
| API | 8000 | FastAPI |
| Worker | — | ARQ tareas async |
| Bot | — | Telegram |
| Web | 3000 | Next.js |
| Adminer | 8080 | DB inspector (opcional) |

### 4. Configurar el Bot de Telegram

1. Habla con [@BotFather](https://t.me/BotFather) en Telegram
2. Crea un nuevo bot: `/newbot`
3. Copia el token en `TELEGRAM_BOT_TOKEN` en `.env`
4. El bot arranca automáticamente con Docker

### 5. Conectar nube personal (opcional)

Desde el dashboard en `/settings/cloud`:
1. Elige Google Drive, Dropbox o OneDrive
2. Haz clic en "Conectar" → popup OAuth
3. Autoriza con scope limitado
4. ¡Listo! El sistema subirá tus facturas automáticamente

**Si no conectas nube:** el sistema funciona igual con almacenamiento local + ZIP mensual por correo.

---

## 🤖 Uso del Bot

### Comandos de Telegram

| Comando | Descripción |
|---------|-------------|
| `/start` | Inicia la conversación y onboarding |
| `/status` | Estado del último ticket procesado |
| `/facturas` | Resumen de facturación del mes |
| `/dashboard` | Link al dashboard web |
| `/lista` | Generar lista de compras |
| `/garantias` | Ver garantías activas y por vencer |
| `/resumen` | Resumen financiero del mes |
| `/cloud` | Estado de la nube personal |
| `/settings` | Configuración del bot |
| `/ayuda` | Ayuda y todos los comandos |

### Flujo de uso

```
1. 📸 Toma foto del ticket
2. 📤 Envía por Telegram al bot
3. 🤖 Bot responde:
   "🔄 Procesando ticket...
    🏪 Tienda: Liverpool
    💰 Total: $2,350.00
    📅 Fecha: 15/06/2026
    🔍 Iniciando facturación..."
4. ✅ "Factura obtenida: UUID: ABC123..."
   "📁 Guardada en local + Google Drive"
5. Si hay garantía: "🛡️ Producto con garantía detectado: Colchón - Vence: 15/06/2028"
6. 📊 Dashboard actualizado automáticamente
```

---

## 📊 Módulo Fiscal SAT

> **Objetivo:** Que puedas hacer tus declaraciones mensuales y anuales del SAT **sin depender de un contador**.

### 🧾 ¿Qué hace?

1. **Carga tu Constancia de Situación Fiscal**
   - Extrae automáticamente: RFC, razón social, régimen fiscal, obligaciones, domicilio
   - Detecta tu régimen (606: sueldos, 605: asalariado, 601: general, etc.)

2. **Conecta tus Estados de Cuenta Bancarios**
   - Soporta BBVA, Santander, Banorte (formato OFX y CSV)
   - Detecta ingresos, transferencias, pagos de servicios
   - Clasifica automáticamente ingresos vs. gastos personales vs. del negocio

3. **Calcula Deducciones Personales (Art. 151 LISR)**
   - El sistema analiza cada ticket y te dice:
     - ✅ **Deducible**: gastos médicos, dentales, hospitalarios, colegiaturas, aportaciones a AFORE, seguros de gastos médicos, intereses hipotecarios, donativos
     - ❌ **No deducible**: alimentos, ropa, entretenimiento, viajes personales
     - 💡 **Área de oportunidad**: "Este gasto en farmacia podría ser deducible si pides factura con concepto médico"
   - Calcula el límite anual de deducciones (5% de tus ingresos o ~$15,000 MXN)

4. **Recomendaciones para maximizar devolución**
   - "Estás pidiendo factura como 'Gastos en general' en Liverpool. Si la pides como 'Muebles de oficina' podrías deducirla si estás en RESICO"
   - "Compraste medicamentos en Farmacias Similares sin factura. Podrías deducir hasta $X si la pides con receta médica"
   - "Tus gastos médicos son deducibles solo si pagaste con transferencia o tarjeta, no en efectivo"

5. **Genera Reportes Fiscales**
   - **Reporte mensual** (XLSX + PDF): ingresos, egresos, deducibles, CFDI emitidos y recibidos
   - **Reporte anual**: resumen para tu declaración anual
   - **Cruce de facturas**: detecta facturas que emitiste vs. las que te emitieron
   - **Formato para contador**: si decides mantener uno, exporta todo listo para que solo firme

### 📋 ¿Qué necesitas para empezar?

1. Tu **Constancia de Situación Fiscal** (descargada del SAT)
2. **Estados de cuenta** de tus bancos (formato PDF/OFX/CSV)
3. **Tus facturas** (el sistema ya las tiene de los tickets procesados)

### 💰 Áreas de Oportunidad Fiscal

El sistema te avisará automáticamente:

| Situación | Problema | Solución |
|-----------|----------|----------|
| Factura como "Gastos en general" | No es deducible específicamente | Pedir con concepto correcto |
| Compra en farmacia sin receta | No aplica como deducción médica | Solicitar receta y factura con diagnóstico |
| Pago en efectivo > $2,000 | No es deducible | Usar tarjeta o transferencia |
| Colegiatura sin factura | Desperdicias deducción automática | Pedir factura con RFC del alumno |
| Renta sin contrato | No puedes deducirla | Formalizar contrato y pedir CFDI de arrendamiento |
| Seguro de gastos médicos sin factura | Pérdida de deducción del 100% | Solicitar factura anual |

---

## 🏪 Multi-negocio y POS

### Para familias con múltiples negocios

- Cada negocio tiene su propio **dashboard, tickets, facturas y análisis**
- Puedes agregar tantos negocios como quieras desde `/settings`
- Los gastos se separan automáticamente por negocio

### Integración con POS (Punto de Venta)

- Cada negocio expone una **API REST independiente**
- El POS puede:
  - Solicitar alta de un nuevo producto o insumo
  - Modificar cantidades
  - Retirar productos
  - Recibir alertas de subidas de precio
- **Dashboard de negocio:**
  - Botón "Meter al carrito" → va al portal del proveedor
  - Si no hay stock: sugiere sustituto o no comprar
  - Genera link del carrito para pago manual
- **Analítica de negocio:**
  - "Compras más caro en Soriana que en Walmart. Ahorrarías $X/mes cambiando"
  - "El precio del huevo subió 15% este mes. Sugerimos ajustar precio al público"

---

## 💾 Almacenamiento y Respaldo

### Flujo completo de un archivo

```
1. 📸 Foto del ticket → /data/storage/tickets/raw/{YYYY}/{MM}/{sha256}.jpg
2. 🤖 OCR procesa → ticket categorizado
3. 🏪 CFDI solicitado → PDF + XML en /data/storage/tickets/cfdi/{uuid}/
4. ☁️ Si hay nube configurada → Sube a Drive/Dropbox/OneDrive
5. 📧 Si NO hay nube → Se incluye en el ZIP mensual
6. 🗑️ Después de 13 meses → Se purga localmente (solo si está en nube o en ZIP)
```

### Retención de datos

| Plazo | Acción |
|-------|--------|
| 0-13 meses | Archivos completos en local + nube (si configurada) |
| >13 meses | Purga local si está en nube. Si no hay nube, se envió por correo |
| Emergencia (<500MB libres) | Purga agresiva a 6 meses automáticamente |

### Monitoreo de cuota de nube

Cada 6 horas el sistema verifica el espacio disponible. Si supera el 90%, notifica por Telegram.

---

## 🚀 Despliegue y CI/CD

### Flujo de trabajo

```bash
# 1. Trabajar en una mejora
git checkout -b feature/mi-mejora
# ... hacer cambios ...
git push origin feature/mi-mejora
# → GitHub Actions corre tests automáticos

# 2. Probar en staging (Mini PC local)
git checkout develop
git merge feature/mi-mejora
git push origin develop
# → Deploy automático a Mini PC con DB de prueba

# 3. Pasar a producción (Hostinger)
git checkout main
git merge develop
git push origin main
# → Backup DB → Deploy → Health Check → Notificación
```

### Una línea para deploy

```bash
# A Mini PC (staging):
git push origin develop

# A Hostinger (producción):
git checkout main && git merge develop && git push origin main
```

### Servicios Docker

```bash
# Iniciar todo
docker-compose up -d

# Ver logs de un servicio
docker-compose logs api
docker-compose logs worker
docker-compose logs bot

# Reiniciar un servicio
docker-compose restart bot

# Ver estado
docker-compose ps
```

---

## 🗺️ Roadmap

| Fase | Estado | Descripción |
|------|--------|-------------|
| **Fase 0** — Setup | ✅ 100% | Monorepo, Docker, CI/CD, documentación |
| **Fase 1** — MVP | 🔄 31% | Tickets, OCR, storage, dashboard básico |
| **Fase 2** — Lista compras | ⏳ 17% | Ciclos de consumo, aprobación familiar, impresión |
| **Fase 3** — CFDI | ✅ 60% | 9 portales, credenciales, Gmail, duplicados |
| **Fase 4** — Multi-negocio | ⏳ 13% | POS API, carrito automático, alertas |
| **Fase 5** — Fiscal SAT | ⏳ 0% | Constancia, deducciones, declaraciones |
| **Testing** | ⏳ 0% | Tests unitarios, E2E, fixtures |
| **Total** | **38%** | **51 de 136 items completados** |

---

## 📚 Documentación adicional

| Documento | Para qué sirve |
|-----------|----------------|
| [docs/ARQUITECTURA_FINAL_v2.md](docs/ARQUITECTURA_FINAL_v2.md) | Decisiones de arquitectura (ARQ, Caddy, multi-tenant). |
| [docs/GUIA_DEPLOY_PASO_A_PASO.md](docs/GUIA_DEPLOY_PASO_A_PASO.md) | Cómo desplegar en Proxmox desde cero. |
| [docs/GUIA_SETUP_WIZARD.md](docs/GUIA_SETUP_WIZARD.md) | Wizard de primera configuración. |
| [docs/GUIA_ACCESO_REMOTO.md](docs/GUIA_ACCESO_REMOTO.md) | Acceso seguro vía Cloudflare Tunnel. |
| [docs/manual/GESTION_SECRETOS.md](docs/manual/GESTION_SECRETOS.md) | **Buenas prácticas de manejo de secretos** (`pass` + GPG + AES-256-GCM). |
| [docs/manual/CHECKLIST_REBRAND_MANUAL.md](docs/manual/CHECKLIST_REBRAND_MANUAL.md) | Checklist de cambios humanos del rebrand. |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Bitácora cronológica del proyecto. |

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

---

> **Iztack-Finance** — *"Dinero Digital"*  
> Hecho en México 🇲🇽 con amor por la independencia financiera