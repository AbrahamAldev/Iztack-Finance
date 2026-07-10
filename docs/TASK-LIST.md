# ✅ Task List — Iztack-Finance

> **Última actualización:** 09/07/2026 — Fase G completada

---

## 📋 Leyenda

| Símbolo | Significado |
|---------|-------------|
| ✅ | Completado |
| 🔄 | En progreso |
| ⏳ | Pendiente |

---

## ✅ Fases Completadas (0-G)

### Fase 0: Admin Portal
- [x] DNS + Cloudflare Access para admfinance.iztack.com
- [x] Modelo StaffUser con roles (super_admin, admin, support, monitor, auditor)
- [x] Login staff JWT (solo @iztack.com)
- [x] Dashboard salud sistema + lista clientes + staff

### Fase 1: Login/Signup con JWT
- [x] Modelo User, password_hash, JWT tokens
- [x] Páginas /login y /register
- [x] AuthGuard en todas las rutas protegidas

### Fase 2: Settings
- [x] Telegram chat_id vinculado por usuario
- [x] Google Drive con credenciales cifradas (AES-256-GCM)
- [x] Barra de capacidad de Drive con alerta

### Fase 3: Subida de tickets
- [x] Selector nativo (iOS: cámara, fototeca, archivos)
- [x] Límite 5MB, preview de imágenes, instrucciones
- [x] Endpoints POST /api/tickets/upload y /upload-base64

### Fase 4: Chat IA
- [x] LLM Client OpenRouter (GPT-4o-mini)
- [x] System prompt anti-prompt-injection
- [x] ChatWidget flotante con contexto real del usuario
- [x] Botón de reporte en chat web

### Fase 5: Telegram multi-usuario
- [x] @IztackFinance_Bot para todos
- [x] Identifica usuarios por chat_id
- [x] LLMClient directo + fallback a comandos predefinidos
- [x] Comando /reporte para enviar bugs a admin

### Fase A: Dashboard con datos reales
- [x] Endpoint GET /api/dashboard con KPIs desde DB
- [x] Gasto mensual, promedio, tickets recientes, warranties

### Fase A.5: Admin Portal avanzado
- [x] Dashboard salud sistema
- [x] Lista de clientes con estado

### Fase B+: Facturación Inteligente
- [x] orchestrator.py — Flujo completo de 10 pasos
- [x] portal_discovery.py — 12 portales conocidos + búsqueda LLM
- [x] portal_learner.py — Playwright + templates JSON
- [x] credential_manager.py — DB real + AES-256-GCM
- [x] fiscal_advisor.py — IA para tipo de gasto
- [x] billing.py — Trigger automático post-OCR
- [x] Modelo FiscalData en DB

### Fase C: Análisis Financiero
- [x] Detección de fugas de dinero (frecuencia + optimización)
- [x] Proyecciones mensuales desde DB real
- [x] Metas de ahorro semanal/mensual

### Fase D: Workers y Notificaciones
- [x] APScheduler integrado en lifespan de FastAPI
- [x] Análisis diario (23:00) con notificación Telegram
- [x] Lista semanal de compras (domingo 08:00)
- [x] Alertas de garantías por vencer (09:00 diario)

### Fase E: Features Adicionales
- [x] Modo oscuro/claro con persistencia local
- [x] Multi-negocio familiar (CRUD + endpoints)
- [ ] Impresora térmica ESC/POS (requiere hardware)
- [ ] Pre-orden en línea (requiere API keys de tiendas)

### Fase F: Módulo Fiscal México
- [x] Subida de CSF (PDF) con extracción LLM
- [x] CRUD de datos fiscales (RFC, régimen, razón social)
- [x] Reglas de deducciones por régimen (LISR Art. 151)
- [x] Endpoints: GET/PUT /api/fiscal/data, POST /api/fiscal/csf/upload

### Fase G: Escalabilidad
- [x] PWA manifest.json para instalación
- [x] Auto-deploy vía cron local cada 5 min
- [x] GitHub Actions deploy deshabilitado (red local)
- [ ] Scripts de backup automático de DB
- [ ] Tests automatizados

---

## ⏳ Pendientes (requieren hardware/credenciales/interacción humana)

| # | Funcionalidad | Bloqueante |
|---|---------------|------------|
| 1 | **Impresora térmica** | Requiere hardware físico + integración Bluetooth/USB |
| 2 | **Pre-orden en línea** | Requiere API keys de Amazon/Walmart/etc |
| 3 | **WhatsApp** | Pospuesto por costo de Twilio |
| 4 | **Pruebas de facturación real** | Requiere credenciales de portales |
| 5 | **Parser de estados de cuenta bancarios** | Requiere PDFs reales de bancos |
| 6 | **Cálculo de ISR anual** | Requiere datos fiscales completos |
| 7 | **Tests automatizados** | Próximo paso inmediato |

---

## 📊 Resumen de Avance

| Fase | Estado |
|------|--------|
| Fases 0-5 + A + A.5 | ✅ 100% |
| Fase B+ (Facturación Intel.) | ✅ 100% |
| Fase C (Análisis) | ✅ 100% |
| Fase D (Workers) | ✅ 100% |
| Fase E (Features) | ✅ 80% |
| Fase F (Fiscal) | ✅ 100% |
| Fase G (Escalabilidad) | ✅ 60% |

---

## 🎯 Próximo Paso

**Tests automatizados** (API, auth, OCR, integración) + **pruebas manuales del usuario**