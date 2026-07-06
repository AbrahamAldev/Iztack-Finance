# 📋 Checklist de Acciones Manuales — Recambio de Marca Iztack-Tomin → Iztack-Finance

> **Audiencia:** Abraham (propietario del repo y de la infra)
> **Origen:** Tras commit `93fab0a` (rama `feature/rebrand-iztack-finance`) se completó todo el cambio editorial en código y docs. Este documento lista **únicamente** las acciones que requieren UI web, acceso humano o decisiones de proveedor.
> **Backup de seguridad:** `git checkout backup-pre-rebrand-20260706` (commit `b652e32`) en caso de necesitar rollback.

---

## 🎯 Resumen ejecutivo (orden recomendado)

| # | Plataforma | Acción | Tiempo est. |
|---|---|---|---|
| 1 | GitHub | Renombrar repo | 2 min |
| 2 | Local (Mac) | Actualizar remote URL + push | 1 min |
| 3 | GitHub | Actualizar `git clone` en README y configs | 5 min |
| 4 | Cloudflare DNS | Crear `finance.iztack.com` (CNAME al tunnel) | 3 min |
| 5 | Cloudflare Access | Actualizar Access App y políticas Zero Trust | 10 min |
| 6 | Proxmox LXC (CT 101) | Renombrar carpeta `/opt/iztack-tomin` → `/opt/iztack-finance` | 5 min |
| 7 | Proxmox LXC (CT 101) | Actualizar `.env` y reiniciar contenedores | 3 min |
| 8 | BotFather (Telegram) | (Opcional) Actualizar nombre/descripción del bot | 3 min |
| 9 | Google Cloud Console | (Opcional) Renombrar proyecto `Iztack-Tomin` | 2 min |
| 10 | Google Drive / Workspace | (Opcional) Renombrar carpetas raíz | 5 min |
| 11 | Apple Wallet / Passwords | (Opcional) Actualizar tags | 5 min |
| 12 | Comunicación | Anunciar nuevo nombre (equipo, contador, familia) | 10 min |

**Tiempo total estimado:** ~55 minutos (sin contar propagación DNS ni comunicación).

---

## 1. 🐙 GitHub — Renombrar el repositorio

**URL actual:** https://github.com/AbrahamAldev/Iztack-Tomin
**URL nueva:** https://github.com/AbrahamAldev/Iztack-Finance

### Pasos

1. Abre https://github.com/AbrahamAldev/Iztack-Tomin en tu navegador (debes estar autenticado como owner).
2. Click en la pestaña **Settings** (esquina superior derecha, junto a "Insights").
3. En la sección **General**, baja hasta el campo **"Repository name"** (es el primero de la página).
4. Borra `Iztack-Tomin` y escribe `Iztack-Finance`.
5. Click en el botón **Rename**.
6. GitHub te redirigirá automáticamente a la nueva URL. Verás un toast verde confirmando.

### ⚠️ Lo que GitHub hace automáticamente
- ✅ Redirige el nombre antiguo al nuevo (HTTP 301) — los `git clone` viejos siguen funcionando durante algunos meses.
- ✅ Mantiene stars, watchers, issues, PRs, releases, tags y branches intactos.
- ✅ Actualiza el `git remote` sugerido en la UI (bot "Code").

### ❌ Lo que GitHub **no** hace
- ❌ No actualiza ningún remote local en tu Mac. **Eso lo haces tú** (paso 2).
- ❌ No renombra Webhooks, Deploy keys, ni GitHub Apps que apunten a la URL vieja (siguen funcionando por el redirect, pero conviene actualizarlos en sus respectivas configuraciones).

---

## 2. 💻 Mac (local) — Actualizar remote URL

Una vez renombrado el repo en GitHub, en tu terminal:

```bash
cd /Users/abraham/Documents/Cursor/Iztack-Tomin

# Ver remote actual
git remote -v
# origin  git@github.com:AbrahamAldev/Iztack-Tomin.git (fetch)
# origin  git@github.com:AbrahamAldev/Iztack-Tomin.git (push)

# Cambiar a la URL nueva (SSH)
git remote set-url origin git@github.com:AbrahamAldev/Iztack-Finance.git

# Verificar
git remote -v
# origin  git@github.com:AbrahamAldev/Iztack-Finance.git (fetch)
# origin  git@github.com:AbrahamAldev/Iztack-Finance.git (push)

# Push de la rama del recambio
git push -u origin feature/rebrand-iztack-finance
```

### Si prefieres HTTPS en lugar de SSH

```bash
git remote set-url origin https://github.com/AbrahamAldev/Iztack-Finance.git
```

### Verificar que el redirect de GitHub funciona

```bash
git fetch origin
# Debe conectar al nuevo nombre sin errores
```

---

## 3. 🐙 GitHub — Abrir Pull Request a `develop`

1. Ve a https://github.com/AbrahamAldev/Iztack-Finance (o el redirect desde el nombre viejo).
2. Click en el banner amarillo **"Compare & pull request"** que aparece al detectar la rama `feature/rebrand-iztack-finance`.
3. **Base branch:** `develop`
4. **Compare branch:** `feature/rebrand-iztack-finance`
5. Título: `docs(rebrand): Iztack-Tomin → Iztack-Finance`
6. Descripción: pega el cuerpo del commit `93fab0a` (ya está en el CHANGELOG).
7. Click **Create pull request**.
8. Auto-aprueba y haz **Merge** (es solo docs, no toca código de producción).
9. Borra la rama remota (botón morado "Delete branch") — opcional pero recomendado.

---

## 4. ☁️ Cloudflare DNS — Crear `finance.iztack.com`

**Asumimos:** ya existe un Cloudflare Tunnel (probablemente `cloudflared` corriendo en el LXC CT 101) con un CNAME wildcard o específico.

### Opción A: Si usas un CNAME wildcard `*.iztack.com → <tunnel-id>.cfargotunnel.com`

Solo necesitas **actualizar el subdominio antiguo** o agregar el nuevo. DNS records actuales (estimados):

| Tipo | Nombre | Destino | Proxy |
|---|---|---|---|
| CNAME | `app` | `<tunnel-id>.cfargotunnel.com` | Proxied (naranja) |
| CNAME | `*` (o lista) | `<tunnel-id>.cfargotunnel.com` | Proxied (naranja) |

### Pasos

1. Abre https://dash.cloudflare.com y selecciona el dominio `iztack.com`.
2. Click en **DNS** → **Records**.
3. **Opción A — agregar el nuevo y dejar el viejo como redirect temporal:**
   - Click **Add record**:
     - Tipo: `CNAME`
     - Name: `finance`
     - Target: `<tunnel-id>.cfargotunnel.com` (copia el del registro `app` o `*`)
     - Proxy: **Proxied** (icono naranja)
     - TTL: Auto
   - Click **Save**.
4. **Opción B — renombrar el registro viejo (más limpio):**
   - Click en el registro `app` (lápiz/editar).
   - Cambia el campo **Name** de `app` a `finance`.
   - Click **Save**.

### Para que `app.iztack.com` siga funcionando mientras migras (opcional)

Crea un redirect HTTP en el `Caddyfile` o en Cloudflare Rules:

- En Cloudflare Dashboard: **Rules** → **Redirect Rules** → **Create rule**:
  - Name: `app → finance (legacy)`
  - Match: `(http.host eq "app.iztack.com")`
  - Action: **Dynamic redirect** → `concat("https://finance.iztack.com", http.request.uri.path)`
  - Status: 301

---

## 5. 🛡️ Cloudflare Access — Actualizar Zero Trust App

**Asumimos:** existe una Access Application llamada "Iztack App" o "Iztack Finance" que protege `app.iztack.com` con email OTP (o similar).

### Pasos

1. Abre https://one.dash.cloudflare.com (Zero Trust dashboard).
2. Click en **Access** → **Applications** (menú izquierdo).
3. Busca la aplicación que protege `app.iztack.com`. Click en su nombre.
4. En la pestaña **Overview**, edita el campo **Application domain**:
   - Quita `app.iztack.com`
   - Agrega `finance.iztack.com`
5. En la pestaña **Policies**:
   - Edita la policy existente.
   - En el campo **Name** o **Selector**, actualiza cualquier referencia a "Iztack-Tomin" → "Iztack-Finance" (cosmético).
6. Click **Save application**.

### Si tienes múltiples Access Apps (uno por servicio: api, web, proxmox, etc.)

Repite los pasos 3-6 para cada una. El archivo `docs/GUIA_ACCESO_REMOTO.md` ya tiene la lista de subdominios.

### Para mantener `app.iztack.com` accesible durante la transición

Duplica la Access App (botón **Add application** → **Self-hosted**):
- Application domain: `app.iztack.com`
- Reusa la misma policy.
- Esto crea un segundo túnel de auth que puedes apagar después de 30 días.

---

## 6. 🖥️ Proxmox LXC (CT 101) — Renombrar carpeta de instalación

**Asumimos:** el contenedor Proxmox CT 101 tiene la app en `/opt/iztack-tomin/`.

### Pasos (ejecuta como root en el LXC, vía SSH o consola Proxmox)

```bash
# 1. SSH al LXC
ssh root@<ip-ct101>   # o entrar por consola web de Proxmox

# 2. Verificar la ruta actual
ls -la /opt/iztack-tomin/

# 3. Apagar contenedores Docker (para evitar archivos en uso)
cd /opt/iztack-tomin
docker compose down

# 4. Renombrar carpeta
mv /opt/iztack-tomin /opt/iztack-finance

# 5. Entrar y revisar .env
cd /opt/iztack-finance
cat .env | head -50
```

### Actualizar el `.env`

Edita `/opt/iztack-finance/.env` (usa `nano`, `vim` o el editor que prefieras):

```bash
nano .env
```

Busca y reemplaza todas las apariciones de `iztack-tomin` por `iztack-finance` en:

| Variable (probable) | Valor nuevo |
|---|---|
| `COMPOSE_PROJECT_NAME` | `iztack-finance` |
| `DATA_DIR` | `/opt/iztack-finance/data` |
| `APP_BASE_URL` | `https://finance.iztack.com` |
| `TELEGRAM_BOT_WEBHOOK_URL` | `https://finance.iztack.com/api/telegram/webhook` |
| `CLOUDFLARE_TUNNEL_HOSTNAME` | `finance.iztack.com` |
| `FRONTEND_URL` | `https://finance.iztack.com` |

> 💡 **Tip:** usa `sed` para hacerlo en una línea:
> ```bash
> sed -i 's/iztack-tomin/iztack-finance/g' .env
> sed -i 's/app\.iztack\.com/finance.iztack.com/g' .env
> ```
> Después revisa el resultado con `cat .env` y ajusta lo que no aplique.

### Reiniciar

```bash
docker compose up -d
docker compose ps      # verifica que todos los servicios estén "Up"
docker compose logs -f api   # revisa que no haya errores de path
```

---

## 7. ☁️ Cloudflare Tunnel — Actualizar ingress

**Asumimos:** el tunnel tiene un `config.yml` en `/etc/cloudflared/` o similar.

### Pasos

```bash
# En el LXC
cat /etc/cloudflared/config.yml
```

Verás algo así:

```yaml
ingress:
  - hostname: app.iztack.com
    service: http://api:8000
  - hostname: api.iztack.com
    service: http://api:8000
  - hostname: proxmox.iztack.com
    service: http://proxmox:8006
  - service: http_status:404
```

Edita y reemplaza los hostnames:

```bash
nano /etc/cloudflared/config.yml
```

| Hostname viejo | Hostname nuevo |
|---|---|
| `app.iztack.com` | `finance.iztack.com` |
| `api.iztack.com` | (mantener o cambiar a `api.finance.iztack.com` según prefieras) |
| `proxmox.iztack.com` | (mantener o `proxmox.finance.iztack.com`) |

Reinicia el servicio del tunnel:

```bash
systemctl restart cloudflared
systemctl status cloudflared
cloudflared tunnel info iztack-finance   # o el nombre que tenga
```

---

## 8. 🤖 BotFather (Telegram) — Renombrar el bot

**Asumimos:** el bot ya está creado y configurado (token en `.env` como `TELEGRAM_BOT_TOKEN`).

### Pasos

1. Abre Telegram y busca **@BotFather** (verificado con palomita azul).
2. Envía el comando: `/mybots`
3. Selecciona el bot actual de Iztack-Tomin.
4. Click en **Edit Bot** → **Edit Name**:
   - Nombre actual (probable): `Iztack-Tomin Bot` o similar
   - Nombre nuevo: `Iztack-Finance`
5. Click en **Edit Bot** → **Edit Description**:
   - Descripción nueva: `Bot financiero personal: tickets, facturas CFDI, garantías, lista de compras, análisis de gastos.`
6. Click en **Edit Bot** → **Edit About**:
   - About nuevo: `Iztack-Finance — tu CFO personal automatizado.`
7. (Opcional) **Edit Bot** → **Edit Commands**:
   - Revisa la lista de comandos (`/start`, `/help`, `/factura`, etc.) y actualiza el `/help` si menciona el nombre viejo.

### ⚠️ Lo que **no** cambia
- ❌ El **token** del bot (`TELEGRAM_BOT_TOKEN`) sigue siendo el mismo. No lo regeneres.
- ❌ El **username** del bot (`@iztack_tomin_bot` o similar) **no se puede cambiar** por diseño de Telegram. Si quieres un username limpio, tendrías que:
  1. Crear un bot nuevo con `@BotFather` → `/newbot` → nombre `IztackFinanceBot`.
  2. Obtener su token nuevo.
  3. Actualizar `TELEGRAM_BOT_TOKEN` en `.env` del LXC.
  4. Hacer `docker compose restart telegram-bot`.
  5. Decirle a tus usuarios que migren al bot nuevo (anuncio en el grupo familiar).

---

## 9. ☁️ Google Cloud Console — Renombrar proyecto (opcional)

**Asumimos:** tienes un proyecto GCP para el OAuth de Google Drive y/o Gmail API.

### Pasos

1. Abre https://console.cloud.google.com/
2. En el selector de proyectos (esquina superior izquierda), selecciona el proyecto `Iztack-Tomin` (o el ID que uses).
3. Click en el menú hamburguesa ☰ → **IAM & Admin** → **Settings**.
4. Click en **Rename** junto a "Project name".
5. Escribe `Iztack-Finance`.
6. Click **Save**.

### ⚠️ El **Project ID** no se puede cambiar
- ❌ El ID técnico (ej. `iztack-tomin-12345`) sigue siendo el mismo.
- ❌ El OAuth Client ID y Client Secret siguen siendo los mismos.
- ✅ No tienes que regenerar credenciales.

### Si también quieres mover el proyecto a otra organización GCP

(Esto ya es fuera de alcance, solo menciónalo si te interesa.)

---

## 10. 📁 Google Drive / Workspace — Renombrar carpetas

**Asumimos:** tienes una estructura tipo:

```
Mi unidad/
└── Iztack-Tomin/
    ├── Facturas/
    │   ├── 2026-06/
    │   └── 2026-07/
    ├── Garantías/
    ├── Tickets Vencidos/
    └── Dañados/
```

### Pasos

1. Abre https://drive.google.com
2. Navega a la carpeta `Iztack-Tomin` (raíz).
3. Click derecho → **Rename** (o click en el nombre y edita).
4. Renombra a `Iztack-Finance`.
5. Repite para subcarpetas si lo deseas (ej. `Iztack-Tomin/Facturas` → `Iztack-Finance/Facturas`) — **opcional**, depende de tu nivel de orden.
6. **Compartir con el contador:**
   - Click derecho en `Iztack-Finance` → **Share** → ingresa el email del contador.
   - Rol: **Viewer** (o **Editor** si también quiere subir).
   - Marca **"Notify people"** si quieres que le llegue email.

### ⚠️ Si el contador tenía bookmark al link viejo
- Drive **redirige automáticamente** del nombre viejo al nuevo por 30 días.
- Pasado ese tiempo, el link se rompe y hay que reenviarlo.

---

## 11. 🍎 Apple Wallet / Apple Passwords — Actualizar tags

### Apple Passwords (iCloud Keychain)

1. Abre **Settings** → **Passwords** (en iPhone/iPad/Mac).
2. Busca las entradas con usuario tipo `iztack-tomin` o notas que mencionen "Iztack-Tomin".
3. Edita cada una:
   - Campo **Notes**: cambia "Iztack-Tomin" → "Iztack-Finance".
   - Campo **URL**: si guardaste `https://app.iztack.com`, actualiza a `https://finance.iztack.com`.
4. Para passwords generadas por el bot de portales de facturación (Walmart, Liverpool, IKEA, etc.):
   - Las passwords no cambian (son de esos portales, no tuyas).
   - Solo actualiza la **carpeta/etiqueta** si usas tags (probable: "Iztack-Tomin" → "Iztack-Finance").

### Apple Wallet (si tienes tarjetas de regalo o membresías)

- Generalmente no aplica a un rebrand, pero si guardaste tarjetas de la marca "Iztack" como programa de lealtad, solo edita el nickname.

---

## 12. 📣 Comunicación — Anunciar el cambio

### A quién avisar

| Audiencia | Canal | Mensaje corto |
|---|---|---|
| Tu familia (usuaria de la lista de compras) | WhatsApp / Telegram | "La app ahora se llama Iztack-Finance. Nueva URL: https://finance.iztack.com" |
| Tu contador | Email | "Te he compartido la carpeta `Iztack-Finance` en Drive. La URL antigua `app.iztack.com` seguirá funcionando unos días." |
| Tu yo del futuro | Nota en Apple Notes | "Si ves un link viejo a `iztack-tomin` o `app.iztack.com`, redirígelo a `finance.iztack.com` o `/opt/iztack-finance`." |

### Plantilla de mensaje (WhatsApp / Telegram)

```
Hola! 👋

El sistema financiero personal ahora se llama **Iztack-Finance** (antes Iztack-Tomin).

🔗 Nueva URL: https://finance.iztack.com
📁 Nueva carpeta de Drive: Iztack-Finance
🤖 Bot de Telegram: @IztackFinanceBot (mismo de antes, solo cambia el nombre)

La URL antigua (app.iztack.com) sigue funcionando unos días como redirect.

Si tienes la app en favoritos, actualiza el bookmark.
```

---

## 🔁 Rollback (si algo sale mal)

### Rollback del código (rápido)

```bash
cd /Users/abraham/Documents/Cursor/Iztack-Tomin
git checkout backup-pre-rebrand-20260706   # vuelve al estado pre-cambio
# o
git reset --hard b652e32                   # mismo efecto, otra sintaxis
```

### Rollback del repo en GitHub (si renombraste y quieres volver)

1. Settings → General → **Repository name**: cambia de `Iztack-Finance` de vuelta a `Iztack-Tomin`.

### Rollback del DNS en Cloudflare

1. Borra el record `finance` o renómbralo de vuelta a `app`.
2. Si usaste Redirect Rule, desactívala.

### Rollback del LXC

```bash
cd /opt
mv iztack-finance iztack-tomin
cd iztack-tomin
docker compose down
# restaura el .env viejo (debes tener un backup)
docker compose up -d
```

> ⚠️ **Importante:** haz un backup del `.env` actual antes de cualquier rollback:
> ```bash
> cp /opt/iztack-finance/.env /root/.env.iztack-finance.backup-$(date +%Y%m%d)
> ```

---

## ✅ Checklist de cierre (marca conforme avances)

- [ ] Repo `Iztack-Tomin` renombrado a `Iztack-Finance` en GitHub
- [ ] Remote URL actualizado en Mac (`git remote -v` lo confirma)
- [ ] Rama `feature/rebrand-iztack-finance` pusheada y PR mergeada a `develop`
- [ ] Cloudflare DNS: `finance.iztack.com` creado y propagado
- [ ] Cloudflare Access: Application domain actualizado a `finance.iztack.com`
- [ ] (Opcional) Redirect rule `app.iztack.com → finance.iztack.com` creado
- [ ] LXC CT 101: `/opt/iztack-tomin` renombrado a `/opt/iztack-finance`
- [ ] LXC CT 101: `.env` actualizado con nuevas URLs
- [ ] LXC CT 101: `docker compose up -d` ejecutado sin errores
- [ ] Cloudflare Tunnel: `config.yml` actualizado, `systemctl restart cloudflared` ejecutado
- [ ] BotFather: nombre, descripción y about del bot actualizados
- [ ] (Opcional) Google Cloud Console: proyecto renombrado
- [ ] (Opcional) Google Drive: carpeta `Iztack-Tomin` renombrada a `Iztack-Finance`
- [ ] (Opcional) Apple Passwords: tags actualizados
- [ ] Familia notificada por WhatsApp/Telegram
- [ ] Contador notificado por email con nuevo link de Drive

---

## 📞 Soporte

Si te atoras en algún paso:
1. Revisa los logs: `docker compose logs -f` en el LXC, o la pestaña **Logs** de Cloudflare Zero Trust.
2. Compara con la guía original `docs/GUIA_DEPLOY_PASO_A_PASO.md` (no se renombró, sigue vigente).
3. Si el problema es de código, abre un issue en el nuevo repo: https://github.com/AbrahamAldev/Iztack-Finance/issues

---

*Generado el 2026-07-06 tras commit `93fab0a` en rama `feature/rebrand-iztack-finance`.*