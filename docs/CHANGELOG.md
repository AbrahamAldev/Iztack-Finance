# 📋 CHANGELOG — Iztack-Tomin

> **Registro cronológico de todas las decisiones, cambios y mejoras hechas en este chat.**
> Propósito: Si se cambia de modelo o chat, este documento permite retomar exactamente donde se quedó.
> Última actualización: 19/06/2026

---

## 📦 Fecha: 19/06/2026 — Sesión Principal

### Cambios de Infraestructura

| # | Cambio | Explicación | Commit |
|---|--------|-------------|--------|
| 1 | **Comparativa arquitectura vs otra IA** | Se analizaron ambas propuestas punto por punto (18 categorías). Se determinó que la otra IA tenía mejor arquitectura general (S3, Tesseract, Caddy, Prometheus) pero el código existente (6,000+ líneas) ya implementaba features más completas (9 portales, garantías, lista familiar, CI/CD). | — |
| 2 | **Adopción de ARQ en lugar de Celery** | ARQ es más simple, Redis-native y mejor integrado con FastAPI async. Se eliminó `celery_app.py`, se creó `apps/worker/main.py` con 7 tareas y `apps/worker/scheduler.py` con 4 tareas periódicas. | `28e70ac` |
| 3 | **Caddy reemplaza a Nginx** | HTTPS automático con Let's Encrypt sin configuración manual. Se creó `infrastructure/caddy/Caddyfile` y se actualizó `docker-compose.yml`. | `28e70ac` |
| 4 | **Almacenamiento híbrido** | Se reemplazó la dependencia exclusiva de Google Drive por un sistema de 4 capas: `LocalStorage` (local), `SensitiveStorage` (cifrado), `RetentionManager` (purga >13 meses), `EmailStorage` (ZIP mensual fallback). | `aac4079` |
| 5 | **Modelos v2 con multi-tenant** | Se rediseñaron los modelos SQLAlchemy de 14 a 18 tablas, agregando `household_id` para soporte multi-negocio/multi-familia. Tablas nuevas: Household, Member, Business, ShoppingListVote, AuditLog, SavingsGoal, MonthlyEmailLog. | `aac4079` |
| 6 | **Scheduler ARQ** | Se creó `apps/worker/scheduler.py` para reemplazar Celery Beat con tareas periódicas nativas de Redis. | `9e2580c` |

### Cambios de Documentación

| # | Cambio | Explicación | Commit |
|---|--------|-------------|--------|
| 7 | **Backup histórico** | `docs/RESUMEN_ARQUITECTURA_COMPLETA.md` → `docs/HISTORICO_ARQUITECTURA_v1.md` para preservar la arquitectura original. | `28e70ac` |
| 8 | **Arquitectura v2** | Se creó `docs/ARQUITECTURA_FINAL_v2.md` con el stack definitivo, flujo CI/CD y tabla de servicios Docker. | `9e2580c` |
| 9 | **Renombre a Iztack-Tomin** | Carpeta renombrada de "Sistema financiero" a "Iztack-Tomin". Iztack = agencia digital, Tomin = "dinero" en Náhuatl. README actualizado. | `b191f86` |
| 10 | **Guía de deploy** | `docs/GUIA_DEPLOY_PASO_A_PASO.md` — Tutorial completo para principiantes con 5 partes: GitHub, Proxmox, contenedor LXC, bot Telegram, flujo diario. | `b191f86` |
| 11 | **IDEA-ORIGINAL.md** | Documento fundacional del proyecto preservado con las 7 secciones primigenias. | `11a1c6f` → renombrado a mayúsculas |
| 12 | **Limpieza de duplicados** | Se eliminó `docs/RESUMEN_ARQUITECTURA_COMPLETA.md` porque era IDÉNTICO a `docs/HISTORICO_ARQUITECTURA_v1.md` (mismos 60,025 bytes). | este commit |
| 13 | **TASK-LIST.md** | Lista maestra de 136 items con estado de avance (38% completado). Subdividido en Fases 0-5 + Infraestructura + Testing + Documentación. | este commit |
| 14 | **CHANGELOG.md** | ESTE DOCUMENTO — Historial de cambios del chat para retomar contexto futuro. | este commit |

### Decisiones Técnicas Tomadas

| Decisión | Opción Elegida | Alternativa Descartada | Razón |
|----------|---------------|----------------------|-------|
| **Workers** | ARQ (Redis nativo) | Celery | Más simple, async-first, sin broker separado |
| **OCR primario** | Tesseract 5 local | Gemini API (único) | Gratuito, offline, suficiente para tickets simples |
| **OCR fallback** | OpenRouter free | Solo Gemini | Agnóstico de proveedor, múltiples modelos free |
| **Storage principal** | Disco local + nube opcional | Solo Google Drive | Más barato, flexible, sin dependencia de API |
| **Reverse proxy** | Caddy | Nginx | HTTPS automático, config mínima |
| **Frontend** | WebApp PWA + Bot Telegram | App nativa iOS/Android | 10x más barato, mismo resultado, sin App Store |
| **Multi-cloud** | Drive/Dropbox/OneDrive | Solo Drive | Elección del usuario, sin vendor lock-in |
| **Email fallback** | ZIP mensual por SMTP | Sin fallback | Si no hay nube, los datos no se pierden |

### Cosas que NO se implementaron (descartadas)

| Feature | Razón | Alternativa |
|---------|-------|-------------|
| WhatsApp en v1 | API restrictiva, requiere aprobación de Meta | Solo Telegram en v1, WhatsApp en v2 |
| Celery + Beat | Complejidad innecesaria | ARQ + Scheduler |
| S3 como storage | Costo adicional innecesario para uso personal | Disco local + nube personal |
| Prometheus/Grafana | Overkill para MVP | Logs de Docker + health checks |
| iCloud | Apple no expone API pública | Instrucciones experimentales para Mac |

### Archivos Creados (resumen)

```
NUEVOS (12 archivos):
apps/worker/__init__.py
apps/worker/main.py             7 tareas ARQ
apps/worker/scheduler.py        4 tareas periódicas
packages/storage/__init__.py
packages/storage/local.py       LocalStorage
packages/storage/sensitive.py   SensitiveStorage (cifrado)
packages/storage/retention.py   RetentionManager (purga)
packages/storage/email_storage.py EmailStorage
packages/shared/__init__.py
packages/shared/models.py       18 tablas v2
infrastructure/docker-compose.yml Caddy + 7 servicios
infrastructure/caddy/Caddyfile  HTTPS automático

DOCUMENTOS (6 archivos):
docs/HISTORICO_ARQUITECTURA_v1.md  Backup v1
docs/ARQUITECTURA_FINAL_v2.md     Stack actual
docs/GUIA_DEPLOY_PASO_A_PASO.md   Tutorial
docs/IDEA-ORIGINAL.md             Visión fundacional
docs/TASK-LIST.md                 Estado de avance
docs/CHANGELOG.md                 ← ESTE DOCUMENTO

ELIMINADOS (1 archivo):
docs/RESUMEN_ARQUITECTURA_COMPLETA.md (duplicado exacto de HISTORICO)
```

### Estado Actual

```
✅ 51 de 136 items completados (38%)
🚀 Listo para subir a GitHub y desplegar en Mini PC
📌 Próximo paso: implementar Tesseract + OpenRouter OCR
```

---

> **Para retomar el proyecto desde cero en otro chat/modelo:**
> 1. Leer `docs/IDEA-ORIGINAL.md` — Visión fundacional
> 2. Leer `docs/TASK-LIST.md` — Estado de avance detallado
> 3. Leer `docs/CHANGELOG.md` — Este documento para contexto
> 4. Leer `docs/ARQUITECTURA_FINAL_v2.md` — Stack actual