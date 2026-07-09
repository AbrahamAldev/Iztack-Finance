# CHANGELOG — Iztack-Finance

> Registro cronológico de todas las decisiones, cambios y mejoras hechas en este chat.
> Propósito: Si se cambia de modelo o chat, este documento permite retomar exactamente donde se quedó.
> Última actualización: 08/07/2026

---

## 📦 Fecha: 08/07/2026 — Sesión: Fases 1-5 completadas + Plan Maestro

### Fase 1: Login/Signup con JWT
- [x] Modelo User con email, password_hash (bcrypt), JWT tokens
- [x] Páginas /login y /register con redirección a dashboard
- [x] AuthGuard para proteger rutas de la app

### Fase 2: Settings (Telegram + Google Drive)
- [x] Vinculación de chat_id de Telegram por usuario
- [x] Google Drive con credenciales cifradas (AES-256-GCM)
- [x] Barra de capacidad de Drive con alerta al 90%

### Fase 3: Subida de tickets con cámara y stitching
- [x] Componente TicketUpload con 3 modos (select, camera, preview)
- [x] Cámara con overlay guía (marco con esquinas)
- [x] Stitching multi-imagen con OpenCV ORB feature matching
- [x] Checkbox "es continuación" para unión automática

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
- [x] get_db_sync() para sesiones síncronas de BD

### CI/CD y correcciones
- [x] deploy.yml: path corregido a /opt/iztack-finance
- [x] ci.yml: build-docker con continue-on-error
- [x] appleboy/ssh-action en todos los workflows
- [x] Secrets configurados (PROXMOX_CT_HOST, PROXMOX_CT_SSH_KEY)

### Landing page SaaS
- [x] 12 features orientadas al usuario final
- [x] Pricing (Básico/Pro/Familiar)
- [x] CTAs, hero, footer

### Plan Maestro definido (pendientes)
- [ ] Fase 0: Setup Admin Portal (admfinance.iztack.com)
- [ ] Fase A: Dashboard con datos reales
- [ ] Fase A.5: Admin Dashboards (salud + clientes)
- [ ] Fase B: Facturación completa
- [ ] Fase C: Análisis financiero
- [ ] Fase C.5: Admin staff + configuración
- [ ] Fase D: Workers + notificaciones + alertas garantía
- [ ] Fase E: Features adicionales
- [ ] Fase F: Módulo Fiscal México (con IA)
- [ ] Fase G: Escalabilidad

---

## 📦 Fecha: 06/07/2026 — Sesión: Gestión de Secretos con `pass` + GPG

| # | Cambio | Explicación | Commit |
|---|--------|-------------|--------|
| 28 | **Manual `docs/manual/GESTION_SECRETOS.md`** | Guía completa de las 4 capas: `pass`+GPG en disco → env vars en RAM → AES-256-GCM en BD → wizard sin mostrar secretos. Inventario de secretos, rotación de `SECRET_KEY`, qué hacer si te roban la laptop, checklist de "lo que NUNCA debes hacer". | este commit |
| 29 | **Script `scripts/load_secrets.sh`** | Carga secretos desde `pass` y arranca `uvicorn` con ellos en ENV. Los valores nunca se loguean ni se persisten a disco. | este commit |

---

## 📦 Fecha: 06/07/2026 — Sesión: Corrección de CHANGELOG + Validación de repo real + Resiliencia post-corte

### Aclaración: el repo correcto es `AbrahamAldev/Iztack-Finance`

| # | Cambio | Explicación | Commit |
|---|--------|-------------|--------|
| 30 | **Verificación: no hay repo `ABRAHAM-ABIZTACK/Iztack-Finance`** | El repo en GitHub del usuario real es `AbrahamAldev/Iztack-Finance`, accesible por SSH (`git@github.com:AbrahamAldev/Iztack-Finance.git`). El remote local ya apunta ahí desde el recambio editorial del 93fab0a. | — |
| 31 | **Corrección de CHANGELOG (entradas #30-#32 anteriores eran erróneas)** | Se había documentado un push a un repo inexistente. Se reemplaza por la realidad: el remote `AbrahamAldev/Iztack-Finance` es el correcto, el push se hace contra ese. | este commit |
| 32 | **Tag `backup-pre-rebrand-20260706` (preservado)** | Sigue en el repo apuntando al commit `b652e32` (antes del recambio de marca). Verificado con `git show-ref --tags`. | `b652e32` (tag) |
| 33 | **Fix del email `noreply` del setup wizard** | El backend usaba un email "demo@..." en el schema de validación; reemplazado por `noreply@iztack.com` que es el dominio real del túnel. | `dd4f9a6` |

### Cambios de Documentación

| # | Cambio | Explicación | Commit |
|---|--------|-------------|--------|
| 34 | **`docs/GUIA_ACCESO_REMOTO.md` — sección de auto-arranque post-corte de luz** | Nueva sección "⚡ Auto-arranque tras corte de luz" con 6 capas de resiliencia. | este commit |
| 35 | **Actualización fecha y "Ver también" en `GUIA_ACCESO_REMOTO.md`** | Fecha → 06/07/2026. | este commit |

---

## 📦 Fecha: 22/06/2026 — Sesión: Setup Wizard + Acceso Remoto Seguro

### Cambios de Frontend

| # | Cambio | Explicación | Commit |
|---|--------|-------------|--------|
| 12 | **Wizard `/setup` con 4 pasos** | Página completa para introducir Telegram/Gemini/Google paso a paso. | este commit |
| 13 | **Fix `/settings` (default export missing)** | Se creó con UI completa: tenant, moneda, zona horaria, impresora. | este commit |

### Cambios de Backend

| # | Cambio | Explicación | Commit |
|---|--------|-------------|--------|
| 14 | **Módulo `setup/`** | Nuevo paquete con routes, service, schemas, tests. Cifrado AES-256-GCM. | este commit |
| 15 | **Tablas `tenants` + `telegram_chat_links`** | Multi-tenant support. | este commit |
| 16 | **Router setup en `main.py`** | Registrado bajo prefix `/api/setup`. | este commit |

### Cambios de Infraestructura

| # | Cambio | Explicación |
|---|--------|-------------|
| 17 | **Acceso SSH con clave Ed25519** | Par de claves generado, alias `ssh proxmox` configurado. |
| 18 | **Inspección Proxmox completa** | CT 101, CT 103, CT 200 mapeados. |
| 19 | **🔐 Acceso remoto seguro vía Cloudflare Tunnel** | Túnel con SSH + Proxmox UI. 5 entradas DNS CNAME. |
| 20 | **`cloudflared` instalado en Mac** | Cliente de Cloudflare Tunnel vía brew. |
| 21 | **Alias SSH `proxmox-remote`** | ProxyCommand con cloudflared access tcp. |

---

## 📦 Fecha: 19/06/2026 — Sesión Principal

### Cambios de Infraestructura

| # | Cambio | Explicación | Commit |
|---|--------|-------------|--------|
| 1 | **Comparativa arquitectura vs otra IA** | 18 categorías analizadas. | — |
| 2 | **Adopción de ARQ en lugar de Celery** | ARQ es más simple, Redis-native. | `28e70ac` |
| 3 | **Caddy reemplaza a Nginx** | HTTPS automático. | `28e70ac` |
| 4 | **Almacenamiento híbrido** | 4 capas: Local, Sensitive, Retention, Email. | `aac4079` |
| 5 | **Modelos v2 con multi-tenant** | 18 tablas con `household_id`. | `aac4079` |
| 6 | **Scheduler ARQ** | Reemplaza Celery Beat. | `9e2580c` |

### Cambios de Documentación

| # | Cambio | Commit |
|---|--------|--------|
| 7 | Backup histórico (`HISTORICO_ARQUITECTURA_v1.md`) | `28e70ac` |
| 8 | Arquitectura v2 (`ARQUITECTURA_FINAL_v2.md`) | `9e2580c` |
| 9 | Renombre a Iztack-Finance | `b191f86` |
| 10 | Guía de deploy | `b191f86` |
| 11 | IDEA-ORIGINAL.md | `11a1c6f` |
| 12 | Recambio editorial Iztack-Tomin → Iztack-Finance | `93fab0a` |
| 13 | CHECKLIST_REBRAND_MANUAL.md | `93fab0a` |