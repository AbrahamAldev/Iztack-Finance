# 📋 Checklist de Acciones — Recambio de Marca Iztack-Tomin → Iztack-Finance

> **Audiencia:** Abraham (propietario del repo y de la infra)
> **Origen:** Recambio editorial completado en commit `93fab0a` (rama `feature/rebrand-iztack-finance`).
> **Backup de seguridad:** `git checkout backup-pre-rebrand-20260706` (commit `b652e32`).

---

## 🔐 Sobre los secretos (importante, léeme primero)

**Esta guía NO contiene ni contendrá tokens, API keys ni passwords.** Por seguridad, los secretos se guardan en:

- **Opción A (recomendada):** un gestor de secretos (`1Password CLI`, `Apple Keychain`, `Bitwarden`, `Doppler`).
- **Opción B:** el archivo `.env` del proyecto (ya está excluido de Git por convención en `.gitignore`).
- **Opción C (NO recomendada):** un archivo de texto plano, aunque sea "local". Se sincroniza por accidente, se captura en screenshots, queda en el historial de Git si se sube, y es vulnerable a compromiso de la máquina.

**¿Cómo opero yo con secretos?**
Si quieres que automatice una acción (renombrar repo, crear DNS, etc.), **te pido el token en este chat en el momento**, lo uso y te recomiendo borrarlo de tu copia local tras la operación. No lo guardo en archivos del repo.

---

## 🤖 Acciones que la IA ya completó automáticamente

| # | Acción | Estado |
|---|---|---|
| ✅ | Recambio editorial en código y docs (10 archivos) | Commit `93fab0a` |
| ✅ | Reescritura de etimología en `README.md` | Commit `93fab0a` |
| ✅ | Filas #12 y #13 en `CHANGELOG.md` | Commit `d8c2c94` |
| ✅ | Tag de backup `backup-pre-rebrand-20260706` (commit `b652e32`) | Local |
| ✅ | Verificación: 0 menciones de "tomin" en el repo | Local |

---

## 🤖 Acciones que la IA PUEDE automatizar (si le pasas el token)

Si quieres que ejecute alguna de estas, dime el ID (A1, A2, …) y te pediré el token correspondiente **en este chat**, en el momento. No se guarda nada en archivos.

| ID | Acción | Herramienta | Credencial que necesito |
|---|---|---|---|
| **A1** | Renombrar repo `Iztack-Tomin` → `Iztack-Finance` en GitHub | `gh repo rename` | `GH_TOKEN` (Personal Access Token con scope `repo`) |
| **A2** | Push de la rama `feature/rebrand-iztack-finance` | `git push` | Ninguna (usa tu SSH key ya configurada) |
| **A3** | Crear PR de la rama → `develop` | `gh pr create` | Mismo `GH_TOKEN` |
| **A4** | Crear DNS record `finance.iztack.com` (CNAME al tunnel) en Cloudflare | `curl` a API v4 | `CF_API_TOKEN` (permiso `Zone.DNS:Edit`) + `CF_ZONE_ID` |
| **A5** | Actualizar Cloudflare Access App (cambiar dominio a `finance.iztack.com`) | API Zero Trust | `CF_API_TOKEN` + `CF_ACCOUNT_ID` |
| **A6** | Renombrar `/opt/iztack-tomin` → `/opt/iztack-finance` en CT 101 | SSH | Ninguna (usa tu alias `ssh proxmox`) |
| **A7** | Actualizar `/opt/iztack-finance/.env` con nuevas URLs y reiniciar Docker | SSH | Ninguna |
| **A8** | Actualizar `/etc/cloudflared/config.yml` (ingress) en CT 103 | SSH | Ninguna |
| **A9** | Renombrar proyecto en Google Cloud Console | `gcloud projects update` | `GOOGLE_APPLICATION_CREDENTIALS` (service account JSON) |
| **A10** | Renombrar carpeta raíz en Google Drive (compartir con contador) | API de Drive | OAuth token con scope `drive` |
| **A11** | Crear bot nuevo `@IztackFinanceBot` en BotFather y devolverte el token | `@BotFather` vía `telegram-cli` o manual | El token del bot actual (para migrar suscriptores) |

> 💡 **Tip de seguridad:** tras usar un token en este chat, cópialo a tu gestor de secretos y bórralo de la conversación que tengas abierta. Así no queda ni siquiera en el portapapeles.

---

## 👤 Acciones ESTRICTAMENTE manuales (solo tú puedes hacerlas)

Estas acciones **no se pueden automatizar de forma fiable** (o requieren tu juicio personal). Por eso quedan en tu lista.

### M1. 🤖 BotFather (Telegram) — Renombrar el bot actual

**Por qué es manual:** La API de BotFather no es REST estándar. Requiere enviar comandos a un bot conversacional. Hay workarounds con `telegram-cli` o `tdlib`, pero son frágiles y cambian sin aviso. Mejor hacerlo a mano en 3 minutos.

**Pasos:**

1. Abre Telegram y busca **@BotFather** (verificado con palomita azul).
2. Envía: `/mybots`
3. Selecciona el bot actual de Iztack-Tomin.
4. **Edit Bot** → **Edit Name**: `Iztack-Finance`
5. **Edit Bot** → **Edit Description**: `Bot financiero personal: tickets, facturas CFDI, garantías, lista de compras, análisis de gastos.`
6. **Edit Bot** → **Edit About**: `Iztack-Finance — tu CFO personal automatizado.`
7. (Opcional) **Edit Bot** → **Edit Commands**: revisa `/help`.

> ⚠️ El **username** del bot (`@iztack_tomin_bot` o similar) **NO se puede cambiar**. Si quieres uno limpio, hay que crear un bot nuevo: `/newbot` → `IztackFinanceBot`. Esa creación sí te la puedo automatizar (A11) si me pasas el contexto.

### M2. 🍎 Apple Passwords — Actualizar tags y URLs guardadas

**Por qué es manual:** Apple Passwords no expone API pública estable. Aunque hay herramientas `security(1)` en macOS para leer el keychain, manipular entradas programáticamente es frágil y Apple no lo soporta oficialmente.

**Pasos:**

1. iPhone/iPad/Mac: **Settings** → **Passwords**.
2. Busca entradas con notas "Iztack-Tomin" o URL `app.iztack.com`.
3. Edita cada una:
   - **Notes:** Iztack-Tomin → Iztack-Finance
   - **URL:** `https://app.iztack.com` → `https://finance.iztack.com`
4. Si usas tags/etiquetas, cámbialos.

### M3. 📣 Comunicación — Anunciar el cambio

**Por qué es manual:** Es una decisión tuya a quién, cuándo y cómo avisar.

**Audiencia sugerida:**

| Audiencia | Canal |
|---|---|
| Familia (usuaria de la lista de compras) | WhatsApp / Telegram |
| Contador | Email |
| Tu yo del futuro | Nota en Apple Notes |

**Plantilla:**

```
Hola! 👋

El sistema financiero personal ahora se llama **Iztack-Finance** (antes Iztack-Tomin).

🔗 Nueva URL: https://finance.iztack.com
📁 Nueva carpeta de Drive: Iztack-Finance
🤖 Bot de Telegram: @IztackFinanceBot (mismo de antes, solo cambia el nombre)

La URL antigua (app.iztack.com) sigue funcionando unos días como redirect.

Si tienes la app en favoritos, actualiza el bookmark.
```

### M4. ✅ Verificación final post-migración

**Por qué es manual:** Requiere tu criterio visual y funcional (probar flujos end-to-end).

**Checklist de humo:**

1. Abre `https://finance.iztack.com` en navegador → debe cargar el dashboard.
2. Abre `https://api.finance.iztack.com/api/info` → debe devolver JSON con `status: ok`.
3. Manda `/start` al bot de Telegram → debe responder.
4. Sube un ticket de prueba → debe procesarse y archivar la factura.
5. Verifica que `app.iztack.com` (vieja) redirige a `finance.iztack.com` (si configuraste el redirect).
6. Revisa logs: `docker compose logs -f api` en el LXC, no debe haber errores de path.

---

## 🔁 Rollback (si algo sale mal)

### Código

```bash
cd /Users/abraham/Documents/Cursor/Iztack-Tomin
git checkout backup-pre-rebrand-20260706
```

### Repo en GitHub

Settings → General → **Repository name** → `Iztack-Tomin` (vuelve al nombre viejo).

### DNS en Cloudflare

Borra el record `finance` o renómbralo a `app`.

### LXC

```bash
cd /opt
mv iztack-finance iztack-tomin
cd iztack-tomin
docker compose down
# restaura el .env viejo (de un backup previo)
docker compose up -d
```

> ⚠️ **Antes de rollback:** `cp /opt/iztack-finance/.env /root/.env.iztack-finance.backup-$(date +%Y%m%d)`

---

## ✅ Checklist de cierre

### 🤖 Acciones automatizadas por la IA (marca conforme las pidas)

- [ ] **A1** Repo renombrado en GitHub
- [ ] **A2** Rama `feature/rebrand-iztack-finance` pusheada
- [ ] **A3** PR mergeado a `develop`
- [ ] **A4** DNS `finance.iztack.com` creado y propagado
- [ ] **A5** Cloudflare Access App actualizada
- [ ] **A6** Carpeta renombrada en LXC CT 101
- [ ] **A7** `.env` actualizado y Docker reiniciado
- [ ] **A8** `config.yml` del Cloudflare Tunnel actualizado
- [ ] (Opcional) **A9** Proyecto GCP renombrado
- [ ] (Opcional) **A10** Carpeta de Drive renombrada
- [ ] (Opcional) **A11** Bot nuevo creado en BotFather

### 👤 Acciones estrictamente manuales (marca conforme las hagas)

- [ ] **M1** BotFather: nombre, descripción, about del bot actual actualizados
- [ ] **M2** Apple Passwords: tags y URLs actualizados
- [ ] **M3** Familia notificada por WhatsApp/Telegram
- [ ] **M3** Contador notificado por email con nuevo link de Drive
- [ ] **M4** Verificación final end-to-end OK

---

## 📞 Soporte

Si te atoras:

1. **Logs en vivo:** `docker compose logs -f` en el LXC, o pestaña **Logs** de Cloudflare Zero Trust.
2. **Guía original (no renombrada, sigue vigente):** `docs/GUIA_DEPLOY_PASO_A_PASO.md`.
3. **Issue en el repo:** https://github.com/AbrahamAldev/Iztack-Finance/issues

---

*Actualizado el 2026-07-06 tras commit `d8c2c94`. Versión anterior: ver historial de Git.*