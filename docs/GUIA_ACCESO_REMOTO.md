# 🌐 Guía de Acceso Remoto — Iztack-Finance

> **Controla tu Proxmox y tu app desde cualquier parte del mundo** (café, oficina, hotel, etc.)
> Sin IP pública, sin VPN, sin Tailscale. Solo Cloudflare Tunnel.

**Última actualización**: 06/07/2026

---

## ⚡ Auto-arranque tras corte de luz (resiliencia)

> **Esta sección es la diferencia entre "el sistema vuelve solo" y "tienes que ir a prender la Mac a las 2 AM porque se fue la luz".**

### Filosofía

- **El Proxmox** se enciende solo cuando vuelve la energía (configurado en BIOS como "Restore on AC Power Loss" → Power On). El hipervisor está en un UPS si lo tienes, y el túnel se restablece sin intervención.
- **Los contenedores (CT 101 app, CT 103 tunnel)** arrancan con el host vía `systemctl enable` y dependencias.
- **El Mac (cliente)** NO está siempre encendido. Se conecta bajo demanda.
- **Después de un corte largo** (varias horas), el sistema **se auto-recupera** y queda accesible vía `https://proxmox.iztack.com` y `ssh proxmox-remote` sin que toques nada.

### Capas de auto-arranque

```
Capa 0 — UPS / Regulador
    └─ aguantar 5-15 min sin red eléctrica (ideal; si no, ve a "Capa 0-bis")

Capa 0-bis — Sin UPS
    └─ configurar BIOS del Proxmox en "Power On after AC loss" (ver bloque siguiente)

Capa 1 — Hipervisor Proxmox
    └─ enciende solo → systemd levanta pveproxy y pvedaemon

Capa 2 — Contenedores LXC (CT 101 app, CT 103 tunnel)
    └─ /etc/pve/lxc/*.conf tiene "onboot: 1" → arrancan en orden de boot
    └─ dentro de cada CT, los servicios tienen "systemctl enable ..."

Capa 3 — Dentro de CT 101 (app)
    └─ docker-compose con restart: unless-stopped
    └─ healthchecks reinician contenedores caídos

Capa 4 — Túnel Cloudflare (CT 103)
    └─ cloudflared con "autoupdate: true" y restart=always
    └─ si Cloudflare se cae, reintenta cada 5s; cuando vuelve, reconecta solo

Capa 5 — Agente de IA / ops-ai
    └─ habilitado en systemd con Restart=always y RestartSec=10
    └─ escribe heartbeat en /var/log/ops-ai/heartbeat.log
```

### Verificación rápida después de un corte

Conéctate desde tu Mac (o desde el celular con Termius) y corre:

```bash
# 1. ¿El Proxmox responde por SSH LAN?
ssh proxmox "uptime && pct list"
# Esperado: "up" reciente (minutos), y la lista de CTs con status "running"

# 2. ¿El túnel está vivo?
ssh proxmox "pct exec 103 -- systemctl is-active cloudflared"
# Esperado: "active"

# 3. ¿El backend responde público?
curl -sI https://api.iztack.com/api/health | head -1
# Esperado: "HTTP/2 200"

# 4. ¿La BD arrancó bien?
ssh proxmox "pct exec 101 -- docker logs --tail 5 sf-postgres 2>&1 | grep -i 'ready\|accept'"
# Esperado: línea con "database system is ready to accept connections"

# 5. ¿El bot de Telegram está despierto?
ssh proxmox "pct exec 101 -- docker logs --tail 5 sf-bot 2>&1 | grep -i 'started\|polling'"
# Esperado: "Started polling" o equivalente
```

Si los 5 checks pasan, **el sistema se recuperó solo**. No tienes que hacer nada más.

### Si algo no levantó (script de rescate)

```bash
ssh proxmox "
  pct exec 103 -- systemctl restart cloudflared
  pct exec 101 -- cd /opt/iztack-finance && docker compose up -d
  sleep 15
  pct exec 101 -- docker ps
"
```

### Configurar el Proxmox para auto-encender tras corte de luz

1. Reinicia el Proxmox y entra a la BIOS (Del / F2 al arranque).
2. Busca: **Power Management → After Power Loss** (o "Restore on AC Power Loss").
3. Cambia a **Power On** (no "Last State", no "Stay Off").
4. Guarda y sal.

Si tu Proxmox es un MiniPC con BIOS distinta, busca: "AC Power Recovery" → "Always Power On".

> 💡 **Tip**: Si quieres validar que está bien configurado SIN esperar un corte real, haz `ssh proxmox "systemctl reboot"` y comprueba que a los 2-3 minutos vuelve a estar accesible.

### Monitoreo proactivo (opcional pero recomendado)

Si quieres que el sistema te avise por Telegram cuando algo NO se recuperó, está el módulo de notificaciones del bot. Documentación detallada en `docs/manual/GESTION_SECRETOS.md` y la config de Telegram en el setup wizard (`/setup` en la web).

---

## 🎯 ¿Qué puedes hacer desde fuera?

| URL | Qué hace |
|---|---|
| `https://proxmox.iztack.com` | Interfaz web de Proxmox (crear/editar CTs, ver métricas) |
| `https://api.iztack.com` | Backend de Iztack-Finance (FastAPI) |
| `https://finance.iztack.com` | Frontend (cuando se arregle el publish del puerto 3000) |
| `https://db.iztack.com` | Adminer (cuando se levante) |
| `https://health.iztack.com` | Health check |
| `ssh proxmox-remote` | Terminal SSH al Proxmox desde tu Mac |

---

## 🚀 Setup único (ya hecho, 1 sola vez)

Tu Mac ya tiene todo configurado. Si cambias de Mac, haz esto:

### 1. Generar clave SSH Ed25519 (si no la tienes)

```bash
ssh-keygen -t ed25519 -C "tu-mac-iztack" -f ~/.ssh/id_ed25519_iztrack
```

### 2. Instalar `cloudflared` (cliente de Cloudflare Tunnel)

```bash
brew install cloudflared
```

### 3. Agregar tu clave pública al Proxmox

⚠️ Esto requiere la contraseña UNA vez. Después nunca más.

```bash
ssh-copy-id -i ~/.ssh/id_ed25519_iztrack.pub root@192.168.0.2
```

### 4. Configurar alias SSH en `~/.ssh/config`

```sshconfig
# Iztack-Finance — acceso LAN (cuando estás en casa)
Host proxmox
    HostName 192.168.0.2
    User root
    IdentityFile ~/.ssh/id_ed25519_iztrack
    IdentitiesOnly yes
    StrictHostKeyChecking no
    ServerAliveInterval 60

# Iztack-Finance — acceso REMOTO (cuando estás fuera de casa)
Host proxmox-remote
    HostName ssh.iztack.com
    User root
    IdentityFile ~/.ssh/id_ed25519_iztrack
    IdentitiesOnly yes
    StrictHostKeyChecking no
    ProxyCommand /opt/homebrew/bin/cloudflared access tcp --hostname %h
```

Listo, ya no necesitas hacer nada más.

---

## 📍 Escenarios de uso

### 🏠 Estoy en casa (LAN)

Usa el alias `proxmox`:

```bash
ssh proxmox "docker ps"
ssh proxmox "cd /opt/iztack-finance && git pull"
```

Velocidad: ~5-15ms (red local).

### 🌎 Estoy fuera de casa (café, oficina, hotel, etc.)

Usa el alias `proxmox-remote`:

```bash
ssh proxmox-remote "docker ps"
ssh proxmox-remote "cd /opt/iztack-finance && git pull"
```

Velocidad: ~50-200ms (viaja por internet hasta Cloudflare, baja por el túnel). Suficiente para editar archivos y correr comandos.

`cloudflared` se conecta solo y crea el túnel transparente. No tienes que abrir nada.

### 🖥️ Quiero la interfaz web de Proxmox

Abre en el navegador (cualquier dispositivo, incluido el móvil):

```
https://proxmox.iztack.com
```

Te va a pedir login (root + contraseña del Proxmox). Una vez logueado, tienes control total: crear CTs, ver gráficas de uso, editar archivos, etc.

### 📱 Quiero entrar desde el iPhone / iPad

1. Abre Safari
2. Ve a `https://proxmox.iztack.com`
3. Login con root + contraseña
4. La UI es responsive, funciona en móvil

---

## 🔐 Seguridad

### ¿Qué tan seguro es?

- **SSH**: Autenticación por clave Ed25519 (256 bits, prácticamente imposible de crackear)
- **Túnel Cloudflare**: TLS 1.3 entre cliente ↔ Cloudflare ↔ Proxmox. Nadie puede sniffear.
- **HTTPS**: Certificados válidos de Let's Encrypt vía Cloudflare
- **Catch-all del túnel**: Cualquier hostname que NO esté en el config devuelve 404 (rechazado)

### Mejores prácticas

- ✅ **NO deshabilites PasswordAuthentication en el Proxmox todavía** (lo puedes dejar hasta que termines la transición)
- ✅ Usa el key SSH siempre, evita password en SSH
- ✅ Si pierdes tu Mac, **rota la clave** (`ssh-keygen` + actualiza `authorized_keys` en Proxmox)
- ⚠️ El token de Cloudflare que usamos para crear los DNS records debería **rotarse/eliminar** cuando ya no se use más

### Rotar la contraseña del Proxmox

```bash
# Desde tu Mac (conectado por LAN o remoto)
ssh proxmox "passwd"
# Te pide la actual y la nueva
```

---

## 🛠️ Comandos útiles

### Verificar que el túnel está vivo

```bash
ssh proxmox-remote "systemctl status cloudflared --no-pager | head -5"
```

### Saber cuánto lleva el Proxmox encendido (útil tras un corte)

```bash
ssh proxmox "uptime -p"
# Ej: "up 3 minutes" → acaba de volver de un corte
# Ej: "up 12 days" → lleva más de una semana estable
```

### Ver logs del túnel (en tiempo real)

```bash
ssh proxmox "pct exec 103 -- journalctl -u cloudflared -f"
```

### Reiniciar el túnel (si se traba)

```bash
ssh proxmox "pct exec 103 -- systemctl restart cloudflared"
```

### Abrir un puerto específico desde tu Mac al Proxmox (port forwarding inverso)

```bash
# Por ejemplo, para acceder al adminer del Proxmox que está en localhost:8080 dentro del CT 101
ssh proxmox -L 8080:localhost:8080 -N
# Luego abres http://localhost:8080 en tu navegador
```

---

## 🧯 Troubleshooting

### "No route to host" al intentar SSH directo a `ssh.iztack.com`

**Causa**: Estás intentando SSH directo al puerto 22 de `ssh.iztack.com`. Los túneles Cloudflare NO funcionan así para TCP.

**Solución**: Usa `ssh proxmox-remote` (con el alias) que usa `cloudflared access tcp` automáticamente.

### "Connection refused" al entrar a `https://proxmox.iztack.com`

**Causa**: El Proxmox UI no está corriendo en `192.168.0.2:8006`.

**Diagnóstico**:
```bash
ssh proxmox "systemctl status pveproxy"
```

**Solución**: Si está caído, reinicia:
```bash
ssh proxmox "systemctl restart pveproxy"
```

### `api.iztack.com` responde 502

**Causa**: El backend (puerto 8000) no está corriendo en el CT 101.

**Diagnóstico**:
```bash
ssh proxmox "pct exec 101 -- docker ps -a"
ssh proxmox "pct exec 101 -- docker logs --tail 20 sf-backend"
```

### `cloudflared` no está en el Mac

```bash
brew install cloudflared
```

### Quiero agregar otro subdominio (ej. `notion.iztack.com`)

1. Decidir qué hostname apuntar (LAN IP del servicio)
2. Editar `/etc/cloudflared/config.yml` en el CT 103
3. Agregar entrada en DNS de Cloudflare (con `cloudflared` o manualmente)
4. `systemctl restart cloudflared`

---

## 📊 Arquitectura del túnel

```
┌─────────────────────┐                                 ┌──────────────────────┐
│  Tu Mac (cliente)   │                                 │  Cloudflare Edge     │
│                     │                                 │  (en 300+ ciudades)  │
│  ssh proxmox-remote │  ─── TLS 1.3 ───────────────►   │                      │
│  https://*.iztack   │  ◄─── 200 OK / SSH tunnel ───   │                      │
└─────────────────────┘                                 └──────────────────────┘
                                                                │
                                                                │ QUIC/HTTP2
                                                                ▼
                                                ┌──────────────────────────────┐
                                                │  Tu Proxmox (CT 103)         │
                                                │  cloudflared daemon          │
                                                │                              │
                                                │  Ingress routing:            │
                                                │  • finance.iztack.com  → :3000   │
                                                │  • api.iztack.com  → :8000   │
                                                │  • proxmox.iztack.com → 8006│
                                                │  • ssh.iztack.com   → :22    │
                                                └──────────────────────────────┘
                                                                │
                                                                ▼
                                                ┌──────────────────────────────┐
                                                │  CT 101 (192.168.0.96)       │
                                                │  Docker containers:          │
                                                │  • sf-frontend (:3000)       │
                                                │  • sf-backend  (:8000)       │
                                                │  • sf-postgres (:5432)       │
                                                │  • sf-redis    (:6379)       │
                                                └──────────────────────────────┘
```

---

## 📋 Resumen de URLs y comandos

| Quiero... | URL o comando |
|---|---|
| SSH al Proxmox desde LAN | `ssh proxmox` |
| SSH al Proxmox desde fuera | `ssh proxmox-remote` |
| UI de Proxmox desde LAN | https://192.168.0.2:8006 |
| UI de Proxmox desde fuera | https://proxmox.iztack.com |
| Backend API | https://api.iztack.com/api/health |
| Ver túnel corriendo | `ssh proxmox "pct exec 103 -- systemctl status cloudflared"` |
| Reiniciar túnel | `ssh proxmox "pct exec 103 -- systemctl restart cloudflared"` |
| Ver logs túnel en vivo | `ssh proxmox "pct exec 103 -- journalctl -u cloudflared -f"` |

---

## 🔗 Ver también

- `docs/GUIA_DEPLOY_PASO_A_PASO.md` — Setup inicial del Proxmox
- `docs/GUIA_CLOUDFLARE_TUNNEL.md` — Detalles del túnel
- `docs/CHANGELOG.md` — Cambios del 06/07/2026 (resiliencia post-corte de luz + rebrand Iztack-Finance)
- `docs/manual/GESTION_SECRETOS.md` — Cómo recuperar secretos si el túnel no levanta
- `docs/manual/CHECKLIST_REBRAND_MANUAL.md` — Cambios de marca Iztack-Tomin → Iztack-Finance 
