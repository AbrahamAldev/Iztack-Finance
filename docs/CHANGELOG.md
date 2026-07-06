# CHANGELOG — Iztack-Finance

> Registro cronológico de todas las decisiones, cambios y mejoras hechas en este chat.
> Propósito: Si se cambia de modelo o chat, este documento permite retomar exactamente donde se quedó.
> Última actualización: 22/06/2026

---

## 📦 Fecha: 22/06/2026 — Sesión: Setup Wizard + Acceso Remoto Seguro

### Cambios de Frontend

| # | Cambio | Explicación | Commit |
|---|--------|-------------|--------|
| 12 | **Wizard `/setup` con 4 pasos** | Página completa para introducir Telegram/Gemini/Google paso a paso. Validación en vivo contra el backend, stepper visual, modal "¿Cómo consigo esta credencial?", toggle de visibilidad para secretos. Redirige al dashboard si ya está configurado. | este commit |
| 13 | **Fix `/settings` (default export missing)** | La página existía pero vacía, Next.js lanzaba "The default export is not a React Component". Se creó con UI completa: tenant, moneda, zona horaria, impresora. | este commit |

### Cambios de Backend

| # | Cambio | Explicación | Commit |
|---|--------|-------------|--------|
| 14 | **Módulo `setup/`** | Nuevo paquete `backend/app/modules/setup/` con `routes.py`, `service.py`, `schemas.py`, `tests/`. Endpoints `GET /api/setup/status`, `POST /api/setup/validate`, `POST /api/setup/finalize`. Cifrado AES-256-GCM para secretos en reposo. Reinicio automático del bot al finalizar. | este commit |
| 15 | **Tablas `tenants` + `telegram_chat_links`** | Nuevas tablas SQLAlchemy: `tenants` (nombre, timezone, setup_completed, secretos cifrados), `telegram_chat_links` (mapeo chat_id → tenant_id para multi-tenant). | este commit |
| 16 | **Router setup en `main.py`** | Registrado bajo prefix `/api/setup`. | este commit |

### Cambios de Infraestructura (¡CRÍTICOS!)

| # | Cambio | Explicación | Commit |
|---|--------|-------------|--------|
| 17 | **Acceso SSH con clave Ed25519** | Par de claves (`~/.ssh/id_ed25519_iztrack`) generado en Mac, clave pública instalada en `root@192.168.0.2`. Alias `ssh proxmox` configurado en `~/.ssh/config`. Entrada sin password habilitada. | — (local, no en repo) |
| 18 | **Inspección Proxmox completa** | Mapeados CT 101 (iztack-finance, 5 contenedores sf-* healthy, IP 192.168.0.96), CT 103 (cloudflared daemon nativo, IP 192.168.0.95), CT 200 (ops-ai). | — (diagnóstico) |
| 19 | **🔐 Acceso remoto seguro vía Cloudflare Tunnel** | **HITO MAYOR.** Se extendió el túnel con SSH + Proxmox UI. Creadas 5 entradas DNS CNAME con proxy 🟠 en Cloudflare (app/api/ssh/proxmox/db → tunnel). El config del tunnel apunta al CT 101 (192.168.0.96) para los servicios HTTP y al host (192.168.0.2) para SSH/Proxmox. | — (config en /etc/cloudflared/config.yml) |
| 20 | **`cloudflared` instalado en Mac** | Cliente de Cloudflare Tunnel instalado vía `brew install cloudflared` (v2026.6.1). | — (local) |
| 21 | **Alias SSH `proxmox-remote`** | En `~/.ssh/config`: usa `ProxyCommand /opt/homebrew/bin/cloudflared access tcp --hostname %h` para conectarse al SSH del Proxmox desde cualquier parte del mundo con un solo comando. | — (local) |

### Hallazgos / Deuda técnica

- ⚠️ El repo en el Proxmox está en `/opt/iztack-finance` (no `/Iztack-Finance`).
- ⚠️ El bot actualmente NO persiste tickets en DB, NO clasifica con LLM, NO es multi-tenant. Eso es para el siguiente turn.
- ⚠️ El frontend (puerto 3000) no responde vía tunnel porque el docker-compose no lo publica correctamente al host — pendiente.
- ⚠️ La contraseña de root del Proxmox y el API token de Cloudflare quedaron expuestos en este chat; se recomienda rotarlos al finalizar.

### 📚 Documentación nueva

- `docs/GUIA_ACCESO_REMOTO.md` — **Guía completa** de cómo trabajar desde fuera (URLs, comandos SSH, troubleshooting, arquitectura).

---

## 📦 Fecha: 19/06/2026 — Sesión Principal

### Cambios de Infraestructura

| # | Cambio | Explicación | Commit |
|---|--------|-------------|--------|
| 1 | **Comparativa arquitectura vs otra IA** | Se analizaron ambas propuestas punto por punto (18 categorías). Se determinó que la otra IA tenía mejor arquitectura general (S3, Tesseract, Caddy, Prometheus) pero el código existente (6,000+ líneas) ya implementaba features más completas (9 portales, garantías, lista familiar, CI/CD). | — |
| 2 | **Adopción de ARQ en lugar de Celery** | ARQ es más simple, Redis-native y mejor integrado con FastAPI async. | `28e70ac` |
| 3 | **Caddy reemplaza a Nginx** | HTTPS automático con Let's Encrypt sin configuración manual. | `28e70ac` |
| 4 | **Almacenamiento híbrido** | 4 capas: LocalStorage, SensitiveStorage (cifrado), RetentionManager (purga >13 meses), EmailStorage (ZIP mensual). | `aac4079` |
| 5 | **Modelos v2 con multi-tenant** | 18 tablas con `household_id`. | `aac4079` |
| 6 | **Scheduler ARQ** | Reemplaza Celery Beat. | `9e2580c` |

### Cambios de Documentación

| # | Cambio | Explicación | Commit |
|---|--------|-------------|--------|
| 7 | **Backup histórico** | `docs/HISTORICO_ARQUITECTURA_v1.md`. | `28e70ac` |
| 8 | **Arquitectura v2** | `docs/ARQUITECTURA_FINAL_v2.md`. | `9e2580c` |
| 9 | **Renombre a Iztack-Finance** | Iztack = agencia/marca; Finance = módulo financiero. | `b191f86` |
| 10 | **Guía de deploy** | `docs/GUIA_DEPLOY_PASO_A_PASO.md`. | `b191f86` |
| 11 | **IDEA-ORIGINAL.md** | Documento fundacional. | `11a1c6f` |