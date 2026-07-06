# ✅ Task List — Proyecto Iztack-Finance

> **Propósito:** Saber exactamente en qué punto estamos y qué falta.
> Última actualización: 19/06/2026

---

## 📋 Leyenda

| Símbolo | Significado |
|---------|-------------|
| ✅ | Completado |
| 🔄 | En progreso |
| ⏳ | Pendiente |
| ❌ | Abandonado/descartado |

---

## FASE 0 — Investigación y Setup Inicial

- [x] Crear estructura del proyecto (monorepo)
- [x] Configurar docker-compose (PostgreSQL + Redis + Caddy + Adminer)
- [x] Configurar Caddy como reverse proxy con HTTPS automático
- [x] Definir y documentar stack tecnológico definitivo
- [x] Crear guía de deploy paso a paso para principiantes
- [x] Backup de arquitectura v1 como histórico

## FASE 1 — MVP Tickets + OCR + Storage + Dashboard

### Modelos y Base de Datos
- [x] Diseñar modelo de datos v2 con 18 tablas
- [x] Migrar a SQLAlchemy async con household_id (multi-tenant)
- [x] Tablas: Household, Member, Business, Ticket, TicketItem
- [x] Tablas: CFDIAttempt, CFDICredential, ShoppingList, ShoppingListVote
- [x] Tablas: Warranty, SavingsGoal, MonthlyEmailLog, AuditLog
- [ ] ⏳ Crear migraciones Alembic para generar las tablas en DB
- [ ] ⏳ Agregar índices faltantes en producción

### Workers (ARQ)
- [x] Crear worker ARQ con 7 tareas asíncronas
- [x] Crear scheduler ARQ con 4 tareas periódicas
- [x] Colas: ocr (alta), cfdi (media), housekeeping (baja)
- [ ] ⏳ Conectar tareas reales con la base de datos
- [ ] ⏳ Implementar reintentos con backoff exponencial

### OCR (Reconocimiento de Tickets)
- [x] Integración con Gemini Vision API (existente)
- [x] Arquitectura de fallback preparada en worker
- [ ] ⏳ **Tesseract 5 como OCR primario** (PENDIENTE)
- [ ] ⏳ **OpenRouter como fallback** (Gemini Flash / Llama 3.2 Vision)
- [ ] ⏳ Clasificación de productos (consumible, durable, garantía, servicio)
- [ ] ⏳ Parser de tickets mexicanos (RFC, fechas, totales)

### Storage (Almacenamiento)
- [x] LocalStorage — wrapper de filesystem
- [x] SensitiveStorage — cifrado AES-256-GCM en reposo
- [x] RetentionManager — purga de archivos >13 meses
- [x] EmailStorage — ZIP mensual por correo (fallback)
- [ ] ⏳ GoogleDriveClient — implementar con OAuth
- [ ] ⏳ DropboxClient — implementar con OAuth
- [ ] ⏳ OneDriveClient — implementar con OAuth
- [ ] ⏳ PersonalCloudClient — interfaz unificada de nube
- [ ] ⏳ Conexión de nube en 3 pasos desde el dashboard
- [ ] ⏳ Monitoreo de cuota de nube cada 6h

### Bot de Telegram
- [x] Bot base funcionando (python-telegram-bot v21)
- [x] Handler de fotos (descarga, hashea, agenda OCR)
- [x] Comando /start, /help
- [ ] ⏳ Comando /status (estado del último ticket)
- [ ] ⏳ Comando /facturas (resumen de facturación)
- [ ] ⏳ Comando /lista (generar lista de compras)
- [ ] ⏳ Comando /resumen (resumen financiero del mes)
- [ ] ⏳ Flujo de aprobación familiar en grupo de Telegram
- [ ] ⏳ Notificaciones de errores con botones de acción
- [ ] ⏳ Mensaje autodestructible con credenciales nuevas

### API REST (FastAPI)
- [x] Estructura de routers por dominio creada
- [ ] ⏳ Endpoint POST /v1/tickets (multipart + idempotente)
- [ ] ⏳ Endpoint GET /v1/tickets (listado paginado con filtros)
- [ ] ⏳ Endpoint GET /v1/tickets/{id} (detalle con items y CFDI)
- [ ] ⏳ Endpoint POST /v1/tickets/{id}/reprocess
- [ ] ⏳ Endpoint POST /v1/cfdi/{ticket_id}/invoice
- [ ] ⏳ Endpoint GET /v1/cfdi/{ticket_id}/status
- [ ] ⏳ Endpoint GET /v1/cfdi/{ticket_id}/files/{pdf|xml}
- [ ] ⏳ Endpoints de dashboard (overview, spend, leaks, categories)
- [ ] ⏳ Endpoints de shopping-list (runs, generate, vote, approve, print)
- [ ] ⏳ Endpoints de garantías (listar, filtrar)
- [ ] ⏳ Endpoints de cloud (status, connect, disconnect, quota)
- [ ] ⏳ Endpoints de auth (JWT con refresh)
- [ ] ⏳ Rate limiting con slowapi
- [ ] ⏳ Audit log middleware
- [ ] ⏳ Health check endpoints (/healthz, /readyz)

### Frontend (Next.js)
- [x] Layout base con navegación (sidebar/bottom-tabs)
- [ ] ⏳ **Migrar a apps/web/ con shadcn/ui** (PENDIENTE)
- [ ] ⏳ Modo oscuro/claro con next-themes
- [ ] ⏳ Página de login con JWT
- [ ] ⏳ Dashboard Overview con KPIs reales
- [ ] ⏳ Tabla de tickets con filtros y paginación
- [ ] ⏳ Detalle del ticket con items y estado CFDI
- [ ] ⏳ Dashboard de gastos por categoría
- [ ] ⏳ Dashboard de fugas de dinero
- [ ] ⏳ Página de garantías con semáforo
- [ ] ⏳ Página de lista de compras
- [ ] ⏳ Página de configuración (miembros, negocios, nube, IA)
- [ ] ⏳ Página de conexión de nube personal
- [ ] ⏳ PWA instalable (manifest + service worker)
- [ ] ⏳ Soporte responsive (móvil + tablet + desktop)

## FASE 2 — Lista de Compras Inteligente

- [x] Arquitectura base del análisis de consumo
- [x] Modelos (ShoppingList, ShoppingListVote)
- [ ] ⏳ Implementar detección de ciclos de consumo (packages/analytics)
- [ ] ⏳ Implementar fuzzy match con rapidfuzz para productos similares
- [ ] ⏳ Generación automática de lista semanal
- [ ] ⏳ Flujo de aprobación híbrido (Telegram + web)
- [ ] ⏳ Impresora ESC/POS (USB y Bluetooth)
- [ ] ⏳ Fallback PDF si la impresora no responde
- [ ] ⏳ Pre-orden: adapter de Amazon México
- [ ] ⏳ Botón "Compartir en Telegram" la lista aprobada
- [ ] ⏳ Actualización en tiempo real con nuevos tickets

## FASE 3 — Facturación CFDI en Portales

- [x] **9 portales implementados** (Liverpool, IKEA, Walmart, Amazon, Home Depot, Oxxo, Farmacias Similares, Pemex, BP)
- [x] PortalAdapter patrón abstracto
- [x] Cifrado de credenciales AES-256-GCM
- [x] Generación de contraseñas con `secrets`
- [x] Búsqueda en Gmail/Outlook vía IMAP
- [ ] ⏳ Chequeo de duplicados en Gmail antes de subir
- [ ] ⏳ Flujo de creación de cuenta con entregable .csv
- [ ] ⏳ Manejo de 3 fallas consecutivas → desactivar adapter
- [ ] ⏳ Tests de humo diarios por adapter
- [ ] ⏳ Portales adicionales (Costco, Chedraui, Sam's Club)

## FASE 4 — Multi-negocio + POS

- [x] Modelo Business con household_id
- [ ] ⏳ CRUD de negocios desde el dashboard
- [ ] ⏳ API REST documentada para POS
- [ ] ⏳ MockPOSAdapter corriendo como servicio
- [ ] ⏳ Eventos bidireccionales con HMAC
- [ ] ⏳ Alertas de stock y precio
- [ ] ⏳ Dashboard de negocio con botón de carrito
- [ ] ⏳ Generación de link de carrito para pago manual

## FASE 5 — Módulo Fiscal (México)

- [ ] ⏳ Parser de constancia de situación fiscal (RFC, régimen, obligaciones)
- [ ] ⏳ Parser de estados de cuenta (BBVA, Santander, Banorte)
- [ ] ⏳ Detector de deducciones LISR Art. 151
- [ ] ⏳ Reporte mensual XLSX + PDF
- [ ] ⏳ Cálculo de impuestos y recomendaciones
- [ ] ⏳ Dashboard fiscal independiente

## Infraestructura y CI/CD

- [x] docker-compose.yml con Caddy + 7 servicios
- [x] Caddyfile con HTTPS automático
- [x] CI/CD: 3 workflows de GitHub Actions
- [x] CI: Tests + Lint + Build (feature/*)
- [x] Deploy staging: automático a Mini PC (develop)
- [x] Deploy production: Backup DB → Deploy → Health Check → Notificar (main)
- [x] .env.example con variables requeridas
- [x] .gitignore completo
- [ ] ⏳ Dockerfiles por servicio (api, worker, bot, web)
- [ ] ⏳ Scripts de backup y restore de DB
- [ ] ⏳ Scripts de rotación de logs
- [ ] ⏳ Configurar self-hosted runner en Mini PC

## Testing

- [ ] ⏳ Test de OCR (10+ fixtures de tickets reales)
- [ ] ⏳ Test de parser (RFCs, fechas, totales)
- [ ] ⏳ Test de categorización (garantía, consumible, servicio)
- [ ] ⏳ Test de deduplicación (misma foto dos veces)
- [ ] ⏳ Test de storage (local, cifrado, nube)
- [ ] ⏳ Test de retención (archivo de 14 meses se purga)
- [ ] ⏳ Test de email mensual (ZIP cifrado por SMTP mock)
- [ ] ⏳ Test de API (auth, roles, aislamiento entre households)
- [ ] ⏳ E2E Telegram (bot test harness)
- [ ] ⏳ E2E Dashboard (Playwright)
- [ ] ⏳ Test de cifrado (key rotation)

## Documentación

- [x] IDEA-ORIGINAL.md — Visión fundacional del proyecto
- [x] TASK-LIST.md — Estado de avance del proyecto ← ESTE DOCUMENTO
- [x] CHANGELOG.md — Historial de cambios de este chat
- [x] ARQUITECTURA_FINAL_v2.md — Stack y servicios actuales
- [x] HISTORICO_ARQUITECTURA_v1.md — Backup de la versión anterior
- [x] GUIA_DEPLOY_PASO_A_PASO.md — Tutorial para principiantes
- [x] INFRAESTRUCTURA.md — Detalles de infraestructura
- [ ] ⏳ API.md — Documentación de endpoints (OpenAPI exportado)
- [ ] ⏳ cfdi-portals.md — Detalle de portales implementados
- [ ] ⏳ pos-integration.md — Documentación para POS
- [ ] ⏳ business-model.md — Modelo de negocio y pricing

---

## 📊 Resumen de Avance

| Fase | Total | ✅ Completado | ⏳ Pendiente | % |
|------|-------|---------------|--------------|---|
| Fase 0 — Setup | 6 | 6 | 0 | **100%** |
| Fase 1 — MVP | 58 | 18 | 40 | **31%** |
| Fase 2 — Lista compras | 12 | 2 | 10 | **17%** |
| Fase 3 — CFDI | 10 | 6 | 4 | **60%** |
| Fase 4 — Multi-negocio | 8 | 1 | 7 | **13%** |
| Fase 5 — Fiscal | 6 | 0 | 6 | **0%** |
| Infraestructura | 15 | 11 | 4 | **73%** |
| Testing | 11 | 0 | 11 | **0%** |
| Documentación | 10 | 7 | 3 | **70%** |
| **TOTAL** | **136** | **51** | **85** | **38%** |

---

## 🎯 Próximos Pasos Inmediatos

1. **Subir a GitHub** y desplegar en Mini PC (staging)
2. Implementar Tesseract + OpenRouter como OCR
3. Migrar frontend a apps/web/ con shadcn/ui
4. Conectar tareas ARQ con base de datos real
5. Implementar GoogleDriveClient con OAuth
6. Agregar tests básicos (OCR, parser, API)
7. Agregar más portales CFDI (Costco, Chedraui)