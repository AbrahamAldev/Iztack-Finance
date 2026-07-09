# ✅ Task List — Iztack-Finance

> **Propósito:** Saber exactamente en qué punto estamos y qué falta.
> **Última actualización:** 08/07/2026

---

## 📋 Leyenda

| Símbolo | Significado |
|---------|-------------|
| ✅ | Completado |
| 🔄 | En progreso |
| ⏳ | Pendiente |
| ❌ | Abandonado/descartado |

---

## ✅ Fases Completadas (1-5)

### Fase 1: Login/Signup con JWT
- [x] Modelo User con email, password_hash (bcrypt), JWT tokens
- [x] Páginas /login y /register con redirección a dashboard
- [x] AuthGuard para proteger rutas de la app
- [x] Navbar con logout

### Fase 2: Settings (Telegram + Google Drive)
- [x] Vinculación de chat_id de Telegram por usuario
- [x] Google Drive con credenciales cifradas (AES-256-GCM)
- [x] Barra de capacidad de Drive con alerta al 90%
- [x] Popup de ayuda "¿Cómo obtener tu Chat ID?"

### Fase 3: Subida de tickets con cámara y stitching
- [x] Componente TicketUpload con 3 modos (select, camera, preview)
- [x] Cámara con overlay guía (marco con esquinas)
- [x] Stitching multi-imagen con OpenCV ORB feature matching
- [x] Checkbox "es continuación" para unión automática
- [x] Endpoint POST /api/tickets/upload (multi-file)
- [x] Endpoint POST /api/tickets/upload-base64

### Fase 4: Chat IA con OpenRouter
- [x] utils/llm.py: Cliente OpenRouter con DeepSeek free
- [x] System prompt anti-prompt-injection (fijo, no editable)
- [x] ChatWidget flotante tipo Intercom/Drift
- [x] Soporte para texto y fotos desde el chat
- [x] Contexto real del usuario (tickets, config, shopping lists)
- [x] OPENROUTER_API_KEY configurada en servidor

### Fase 5: Telegram multi-usuario
- [x] Un solo bot @IztackFinance_Bot para todos
- [x] Identifica usuarios por chat_id vinculado en Settings
- [x] Usuarios no vinculados reciben instrucciones para conectar
- [x] Textos con ChatService con IA (OpenRouter)
- [x] Fotos procesadas con OCR
- [x] get_db_sync() para sesiones síncronas de BD

### Infraestructura y CI/CD
- [x] Proxmox CT 101 (app) + CT 103 (tunnel)
- [x] Cloudflare Tunnel con dominios: finance.iztack.com, apifinance.iztack.com
- [x] Docker compose con 5 servicios (postgres, redis, backend, frontend, bot)
- [x] CI/CD: GitHub Actions con appleboy/ssh-action
- [x] Secrets configurados (PROXMOX_CT_HOST, PROXMOX_CT_SSH_KEY)
- [x] Landing page SaaS con 12 features y pricing

---

## 🔄 Plan Maestro — Próximas Fases

### Fase 0: Admin Portal (admfinance.iztack.com)
**Tiempo estimado: ~8.5h**

| # | Tarea | Prioridad |
|---|---|---|
| 0.1 | DNS CNAME admfinance.iztack.com + Tunnel ingress | Alta |
| 0.2 | Cloudflare Access: policy solo emails @iztack.com | Alta |
| 0.3 | Modelo StaffUser (tabla separada con role y permissions bitmask) | Alta |
| 0.4 | Auth staff (login solo @iztack.com, JWT staff, detección de rol) | Alta |
| 0.5 | Layout admin (sidebar, navbar, tema oscuro) | Alta |
| 0.6 | Dashboard salud sistema (servicios Docker, uptime, disco, CPU, RAM) | Alta |
| 0.7 | Lista clientes (ver usuarios, tickets, estado, forzar reprocesos) | Alta |

### Fase A: Dashboard con datos reales
**Tiempo estimado: ~14h**

| # | Tarea | Prioridad |
|---|---|---|
| A.1 | Endpoint GET /api/dashboard (totals, tickets recientes, garantías activas) | Alta |
| A.2 | KPIs conectados a DB en frontend | Alta |
| A.3 | Upload de tickets persiste en tabla Ticket + Product | Alta |
| A.4 | Lista de compras con productos reales desde los tickets | Alta |

### Fase A.5: Admin Portal — Gestión de clientes
**Tiempo estimado: ~9h**

| # | Tarea | Prioridad |
|---|---|---|
| A.5.1 | Ver detalle de cliente (tickets, conversaciones chat, config) | Alta |
| A.5.2 | Forzar reprocesamiento de tickets desde admin | Alta |
| A.5.3 | Suspender/activar cuentas de clientes | Media |
| A.5.4 | Exportar datos del cliente (GDPR compliance) | Media |

### Fase B: Facturación completa
**Tiempo estimado: ~17h**

| # | Tarea | Prioridad |
|---|---|---|
| B.1 | Endpoint POST /api/tickets/{id}/invoice | Alta |
| B.2 | Pantalla de estado de facturación en frontend | Alta |
| B.3 | Creación automática de cuentas en portales | Alta |
| B.4 | Búsqueda en Gmail (fallback cuando el portal falla) | Alta |
| **B.5** | **🌑 Carpeta errores/dañados en Drive** — Tickets no procesables se mueven a /Errores/ con log del error | Media |
| B.6 | Manejo de errores (tickets vencidos, datos ilegibles, sin cuenta) | Alta |

### Fase C: Análisis financiero
**Tiempo estimado: ~14h**

| # | Tarea | Prioridad |
|---|---|---|
| C.1 | Endpoint gastos por categoría | Alta |
| C.2 | Algoritmo de detección de fugas de dinero | Alta |
| C.3 | Dashboard con gráficos (Recharts) | Alta |
| C.4 | Proyecciones de gasto mensual | Media |

### Fase C.5: Admin Portal — Staff + Configuración
**Tiempo estimado: ~11h**

| # | Tarea | Prioridad |
|---|---|---|
| C.5.1 | CRUD de usuarios staff (crear, editar rol, suspender) | Alta |
| C.5.2 | Gestión de roles y permisos (solo super_admin) | Alta |
| C.5.3 | Panel de configuración del sistema (portales on/off, límites) | Alta |
| C.5.4 | Logs en tiempo real con búsqueda | Media |

### Fase D: Workers y Automatización
**Tiempo estimado: ~15h**

| # | Tarea | Prioridad |
|---|---|---|
| D.1 | Conectar workers ARQ con tareas reales | Alta |
| D.2 | Análisis diario (23:00) | Alta |
| D.3 | Lista de compras semanal automática (domingo 08:00) | Alta |
| D.4 | Reporte mensual (día 1) | Media |
| **D.5** | **🌑 Notificaciones compras sin ticket** — Tarea nocturna que pregunta al usuario si compró productos con ciclo vencido pero sin ticket | Media |
| **D.6** | **🌑 Alertas garantía por vencer** — Tarea diaria que revisa garantías activas y alerta si faltan ≤30 días | Media |

### Fase E: Features Adicionales
**Tiempo estimado: ~22h**

| # | Tarea | Prioridad |
|---|---|---|
| E.1 | Multi-negocio familiar (CRUD negocios, API POS) | Media |
| E.2 | Portales CFDI extra (Costco, Chedraui, Sam's Club) | Media |
| E.3 | Impresora térmica ESC/POS (USB + Bluetooth) | Baja |
| E.4 | Modo oscuro/claro (next-themes) | Baja |
| E.5 | Pre-orden en línea (Amazon adapter) | Baja |

> ❌ **E.6 WhatsApp** — Pospuesto. Evaluar impacto económico de Twilio más adelante.

### Fase F: Módulo Fiscal México 🏛️
**Tiempo estimado: ~24h**

| # | Tarea | Prioridad |
|---|---|---|
| F.1.1 | Subir Constancia de Situación Fiscal (PDF) → Parser extrae RFC, Régimen, Obligaciones | Alta |
| F.1.2 | Subir Estados de Cuenta bancarios (PDF/CSV) → Parser extrae ingresos, egresos, saldos | Alta |
| F.1.3 | Subir facturas de gastos deducibles (honorarios médicos, dentales, colegiaturas) | Alta |
| F.1.4 | Guardar todo cifrado (AES-256-GCM) con metadatos de régimen fiscal | Alta |
| F.2.1 | Base de reglas fiscales mexicanas (LISR Art. 151, deducciones personales, topes por régimen) | Alta |
| F.2.2 | Tabla de deducciones por régimen (Sueldos, Honorarios, RESICO, RIF, Arrendamiento) | Alta |
| F.3.1 | Analizador de documentos faltantes — IA detecta qué falta y pide al usuario | Alta |
| F.3.2 | Cálculo de ISR anual estimado con ingresos y deducciones | Alta |
| F.3.3 | Recomendaciones personalizadas de optimización fiscal | Alta |
| F.3.4 | Optimización de facturación — "Pide factura con RFC para deducir" | Media |
| F.3.5 | Reporte fiscal anual PDF con resumen y recomendaciones | Media |
| F.3.6 | Siempre informar al usuario: "Tus datos fiscales están cifrados con AES-256-GCM" | Alta |

### Fase G: Escalabilidad
**Tiempo estimado: ~15h**

| # | Tarea | Prioridad |
|---|---|---|
| G.1 | Scripts de backup y restore de DB | Alta |
| G.2 | PWA instalable (manifest + service worker) | Baja |
| G.3 | Tests de humo (salud del sistema) | Media |
| G.4 | Tests de OCR con fixtures de tickets reales | Media |
| G.5 | Tests de API (auth, roles, aislamiento entre usuarios) | Media |

---

## 📊 Resumen de Avance

| Fase | Tiempo | Completado | % |
|------|--------|------------|---|
| **Fases 1-5** (Completadas) | — | ✅ 100% | **100%** |
| **Fase 0** Admin Portal | 8.5h | ⏳ 0% | **0%** |
| **Fase A** Dashboard real | 14h | ⏳ 0% | **0%** |
| **Fase A.5** Admin clientes | 9h | ⏳ 0% | **0%** |
| **Fase B** Facturación | 17h | ⏳ 0% | **0%** |
| **Fase C** Análisis | 14h | ⏳ 0% | **0%** |
| **Fase C.5** Admin staff | 11h | ⏳ 0% | **0%** |
| **Fase D** Workers | 15h | ⏳ 0% | **0%** |
| **Fase E** Features | 22h | ⏳ 0% | **0%** |
| **Fase F** Módulo Fiscal | 24h | ⏳ 0% | **0%** |
| **Fase G** Escalabilidad | 15h | ⏳ 0% | **0%** |
| **TOTAL PENDIENTE** | **~149.5h** | | |

---

## 🎯 Próximo Paso Inmediato

**Fase 0: Setup Admin Portal (admfinance.iztack.com)**
1. Configurar DNS CNAME + Tunnel ingress
2. Cloudflare Access policy (solo @iztack.com)
3. Modelo StaffUser con roles
4. Login staff con JWT
5. Layout admin con sidebar
6. Dashboard de salud del sistema
7. Lista de clientes