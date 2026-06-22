# 🌐 Guía de Exposición Segura con Cloudflare Tunnel

> **Propósito:** Exponer Iztack-Tomin (o cualquier servicio local) a internet de forma segura usando Cloudflare Tunnel, sin abrir puertos en el router, con protección geográfica y por dispositivo.

---

## 📋 Tabla de Contenidos

1. [¿Qué es Cloudflare Tunnel?](#1-qué-es-cloudflare-tunnel)
2. [Requisitos](#2-requisitos)
3. [Opción A: Contenedor LXC (Recomendado)](#3-opción-a-contenedor-lxc-recomendado)
4. [Opción B: VM Ubuntu](#4-opción-b-vm-ubuntu)
5. [Instalar cloudflared](#5-instalar-cloudflared)
6. [Configurar el Tunnel](#6-configurar-el-tunnel)
7. [Seguridad: Bloquear IPs fuera de México](#7-seguridad-bloquear-ips-fuera-de-méxico)
8. [Seguridad: Acceso por Dispositivo (MAC/WARP)](#8-seguridad-acceso-por-dispositivo)
9. [Probar la conexión](#9-probar-la-conexión)
10. [Mantenimiento](#10-mantenimiento)

---

## 1. ¿Qué es Cloudflare Tunnel?

Cloudflare Tunnel (cloudflared) crea un **túnel cifrado** desde tu servidor local hasta la red de Cloudflare. Esto significa:

- ❌ **No necesitas abrir puertos** en tu router (no más `:8006`, `:3000`, etc.)
- ✅ **HTTPS automático** con certificados de Cloudflare
- ✅ **Protección DDoS** incluida
- ✅ **Bloqueo geográfico** (solo México, por ejemplo)
- ✅ **Autenticación por dispositivo** (solo tus equipos autorizados)
- ✅ **Sin IP pública estática** — funciona aunque tu IP cambie

### Diagrama de funcionamiento:

```
Usuario ──► iztack.com ──► Cloudflare ──═╗ (túnel cifrado)
                                          ║
Mini PC (Proxmox) ──► cloudflared ──═════╝
```

---

## 2. Requisitos

| Recurso | Requerido |
|---------|-----------|
| **Dominio** | Un dominio (ej: `iztack.com`) administrado por Cloudflare |
| **Cuenta Cloudflare** | Gratuita (https://dash.cloudflare.com) |
| **Servidor local** | Mini PC con Proxmox (o cualquier Linux) |
| **Iztack-Tomin** | Desplegado y funcionando en la red local |

### 2.1 Configurar el dominio en Cloudflare

1. Ve a **https://dash.cloudflare.com**
2. Agrega tu dominio: **"Add a Site"** → escribe `tudominio.com`
3. Cloudflare te dará **2 nameservers** (ej: `ns1.cloudflare.com`, `ns2.cloudflare.com`)
4. Ve a **donde compraste el dominio** (GoDaddy, Namecheap, etc.) y cambia los nameservers por los de Cloudflare
5. Espera 5-30 minutos a que se propague

### 2.2 Crear el Token de Tunnel

1. En Cloudflare Dashboard, ve a **Zero Trust** (menú izquierdo)
2. Ve a **Access → Tunnels**
3. Haz clic en **"Create a tunnel"**
4. Ponle nombre: **`iztack-tomin`**
5. Elige **"cloudflared"** como tipo
6. Cloudflare te mostrará un **Token** (se ve así: `eyJhIjoi...`)
7. **COPIA ESE TOKEN** — lo necesitarás después

---

## 3. Opción A: Contenedor LXC (Recomendado)

**Ventajas:** Más ligero que una VM, usa el kernel del host, arranca en segundos.

### 3.1 Crear el contenedor

En la terminal de Proxmox (**>_ Shell**):

```bash
# Descargar template de Ubuntu 22.04 (si no lo tienes)
pveam update
pveam download local ubuntu-22.04-standard_22.04-1_amd64.tar.zst

# Crear contenedor (cambia el ID si el 103 ya está ocupado)
pct create 103 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname cloudflare-tunnel \
  --storage local-lvm \
  --rootfs 4 \
  --cores 1 \
  --memory 512 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --unprivileged 1 \
  --features nesting=1

# Iniciar contenedor
pct start 103

# Entrar al contenedor
pct enter 103
```

### 3.2 Actualizar e instalar cloudflared

```bash
# Actualizar paquetes
apt update && apt upgrade -y

# Instalar dependencias
apt install -y curl wget

# Descargar cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# Instalar
dpkg -i cloudflared-linux-amd64.deb

# Verificar
cloudflared --version
```

---

## 4. Opción B: VM Ubuntu

**Ventajas:** Aislamiento completo, puedes tener su propio kernel.

### 4.1 Crear la VM

En la terminal de Proxmox:

```bash
# Descargar ISO de Ubuntu Server
pveam download local ubuntu-22.04-server-cloudimg-amd64.img

# Crear VM (cambia el ID si el 103 ya está ocupado)
qm create 103 \
  --name cloudflare-tunnel \
  --memory 1024 \
  --cores 1 \
  --net0 virtio,bridge=vmbr0 \
  --scsihw virtio-scsi-pci

# Importar disco
qm importdisk 103 /var/lib/vz/template/iso/ubuntu-22.04-server-cloudimg-amd64.img local-lvm

# Configurar disco
qm set 103 --scsi0 local-lvm:vm-103-disk-0

# Configurar arranque
qm set 103 --boot c --bootdisk scsi0

# Iniciar VM
qm start 103
```

Luego accedes por la consola de Proxmox y completas la instalación de Ubuntu.

---

## 5. Instalar cloudflared

Ya sea que hayas elegido LXC o VM, los siguientes pasos son iguales.

### 5.1 Instalar cloudflared

```bash
# Descargar e instalar
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i cloudflared-linux-amd64.deb

# Verificar
cloudflared --version
```

### 5.2 Autenticar el túnel

```bash
cloudflared tunnel login
```

Esto abrirá un link. Cópialo y pégalo en tu navegador. Autoriza el dominio que configuraste en Cloudflare.

---

## 6. Configurar el Tunnel

### 6.1 Crear el túnel

```bash
# Crear el túnel (nómbralo como quieras)
cloudflared tunnel create iztack-tomin
```

Esto genera un archivo de certificado en `~/.cloudflared/` y te muestra un **UUID** (algo como `12345678-1234-1234-1234-123456789abc`).

### 6.2 Configurar el archivo de túneles

> **⚠️ IMPORTANTE:** El archivo debe crearse en `/etc/cloudflared/config.yml` (NO en `~/.cloudflared/`), porque el servicio systemd de cloudflared busca la configuración en `/etc/cloudflared/`. Si lo creas en `~/.cloudflared/`, el servicio fallará con `exit code 1`.

```bash
# Crear el directorio del sistema
mkdir -p /etc/cloudflared

# Crear el archivo de configuración
nano /etc/cloudflared/config.yml
```

Pega esto (ajusta los puertos según tu configuración):

```yaml
# Configuración de Cloudflare Tunnel para Iztack-Tomin
tunnel: TU-UUID-DEL-TUNNEL
credentials-file: /etc/cloudflared/TU-UUID-DEL-TUNNEL.json

ingress:
  # Frontend (Next.js)
  - hostname: app.tudominio.com
    service: http://IP_DEL_SERVIDOR:3000

  # Backend API (FastAPI)
  - hostname: api.tudominio.com
    service: http://IP_DEL_SERVIDOR:8000

  # Adminer (opcional, base de datos)
  - hostname: db.tudominio.com
    service: http://IP_DEL_SERVIDOR:8080

  # Health check
  - hostname: health.tudominio.com
    service: http://IP_DEL_SERVIDOR:8000

  # Catch-all: rechazar todo lo demás
  - service: http_status:404
```

**Reemplaza:**
- `TU-UUID-DEL-TUNNEL` → el UUID que te mostró el comando anterior
- `IP_DEL_SERVIDOR` → la IP del servidor donde corre Iztack-Tomin
- `tudominio.com` → tu dominio (ej: `iztack.com`)

**⚠️ Cómo saber la IP correcta del servidor:**

> **IMPORTANTE:** Los comandos `pct list` y `pct enter` se ejecutan en la **terminal de Proxmox** (botón **>_ Shell** en la interfaz web del navegador), **NO** dentro del contenedor `cloudflare-tunnel`. Si los escribes dentro del contenedor, verás `Command 'pct' not found`.

```bash
# Desde la terminal de Proxmox (NO desde el contenedor):

# 1. Listar contenedores y sus IDs
pct list

# 2. Ver la IP de un contenedor específico (reemplaza "ID" por el número real, ej: 100, 101, 102)
#    Ejemplo correcto: pct enter 103 -- ip a | grep eth0
#    Ejemplo INCORRECTO: pct enter ID -- ip a | grep eth0  ← "ID" literal no funciona
pct enter NUMERO_DEL_CONTENEDOR -- ip a | grep eth0
```

- Iztack-Tomin corre en el **host Proxmox** → usa la IP del host (ej: `192.168.0.2`)
- Iztack-Tomin corre en un **contenedor separado** → usa la IP de ese contenedor
- **Nota:** El contenedor `cloudflare-tunnel` solo tiene cloudflared. No pongas su IP como destino de los servicios.

**Nota sobre el health check:** No uses rutas como `http://IP:8000/api/health`. Cloudflare Tunnel **no permite** subdirectorios en el `service`. Usa solo la dirección base (`http://IP:8000`).

### 6.3 Crear los registros DNS en Cloudflare

> **⚠️ IMPORTANTE:** Estos comandos se ejecutan **DENTRO del contenedor** `cloudflare-tunnel` (después de `pct enter 103`), **NO** desde la terminal de Proxmox. Si los ejecutas desde Proxmox, verás el error: `Cannot determine default origin certificate path. No file cert.pem`.

```bash
# Primero: entrar al contenedor (desde la terminal de Proxmox)
pct enter 103

# Ya dentro del contenedor (root@cloudflare-tunnel:~#), crear los subdominios:
cloudflared tunnel route dns iztack-tomin app.tudominio.com
cloudflared tunnel route dns iztack-tomin api.tudominio.com
cloudflared tunnel route dns iztack-tomin db.tudominio.com
cloudflared tunnel route dns iztack-tomin health.tudominio.com
```

### 6.4 Iniciar el túnel como servicio

```bash
# Instalar como servicio del sistema
cloudflared service install

# Iniciar
systemctl start cloudflared

# Verificar que está corriendo
systemctl status cloudflared

# Habilitar para que inicie automáticamente
systemctl enable cloudflared
```

### 6.5 Verificar que el túnel funciona

```bash
# Ver logs
journalctl -u cloudflared -f

# Deberías ver algo como:
# INF Connection 0 registered
# INF Connection 1 registered
# INF Connection 2 registered
# INF Connection 3 registered
```

---

## 7. Seguridad: Bloquear IPs fuera de México

### 7.1 Desde Cloudflare Dashboard (recomendado)

1. Ve a **Cloudflare Dashboard → tu dominio → Security → WAF**
2. Haz clic en **"Create rule"**
3. Configura:

```
Rule name: Bloquear fuera de México
Field: Country
Operator: is not in
Value: MX
Action: Block
```

4. Haz clic en **"Deploy"**

### 7.2 Desde la terminal (alternativa)

Si prefieres hacerlo desde la terminal con la API de Cloudflare:

```bash
# Instalar jq para procesar JSON
apt install -y jq

# Obtener el Zone ID de tu dominio
ZONE_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=tudominio.com" \
  -H "Authorization: Bearer TU_API_TOKEN" \
  -H "Content-Type: application/json" | jq -r '.result[0].id')

# Crear regla WAF para bloquear fuera de México
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/firewall/rules" \
  -H "Authorization: Bearer TU_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "block",
    "priority": 1,
    "description": "Bloquear trafico fuera de Mexico",
    "filter": {
      "expression": "(ip.geoip.country ne \"MX\")"
    }
  }'
```

**Para obtener el API Token:**
1. Ve a **https://dash.cloudflare.com/profile/api-tokens**
2. Crea un token con permisos: `Zone:Firewall Services:Edit`
3. Copia el token y úsalo donde dice `TU_API_TOKEN`

---

## 8. Seguridad: Acceso por Dispositivo

### 8.1 Cloudflare WARP (recomendado para dispositivos móviles)

Cloudflare WARP crea una VPN que solo permite acceso a usuarios con el cliente instalado.

1. Ve a **Cloudflare Zero Trust → Settings → WARP Client**
2. Descarga el cliente WARP en tus dispositivos:
   - **Mac:** https://1.1.1.1/
   - **iPhone/iPad:** App Store → "1.1.1.1: Faster Internet"
   - **Android:** Google Play → "1.1.1.1: Faster Internet"
3. En **Zero Trust → Access → Policies**, crea una política:

```
Policy name: Solo dispositivos autorizados
Action: Allow
Session duration: 24h

Rules:
  - Selector: Country → is in → MX
  - Selector: WARP Device ID → is in → [IDs de tus dispositivos]
```

### 8.2 Cloudflare Access (para acceso web)

Puedes requerir autenticación por email o Google para acceder al dashboard:

1. Ve a **Zero Trust → Access → Applications**
2. **"Add an application"** → **"Self-hosted"**
3. Configura:

```
Application name: Iztack-Tomin Dashboard
Domain: app.tudominio.com
Session duration: 24h

Policies:
  - Action: Allow
  - Rule: Emails ending in → @tudominio.com
```

4. Ahora, cuando alguien entre a `app.tudominio.com`, Cloudflare le pedirá **verificar su email** antes de mostrar el dashboard.

### 8.3 Bloquear por IP (para acceso desde casa)

Si solo accedes desde tu casa (IP fija o semi-fija):

1. Ve a **Cloudflare Dashboard → Security → WAF**
2. **"Create rule"**:

```
Rule name: Solo IPs autorizadas
Field: IP Source Address
Operator: is in
Value: [TU_IP_PUBLICA]
Action: Block
```

Para saber tu IP pública:

```bash
curl ifconfig.me
```

---

## 9. Probar la conexión

### 9.1 Verificar el túnel

```bash
# En el servidor cloudflared
systemctl status cloudflared
journalctl -u cloudflared --no-pager | tail -20
```

### 9.2 Probar desde el navegador

| Servicio | URL | Deberías ver |
|----------|-----|--------------|
| Frontend | `https://app.tudominio.com` | Dashboard de Iztack-Tomin |
| API | `https://api.tudominio.com/docs` | Documentación Swagger |
| Health | `https://health.tudominio.com` | `{"status": "healthy"}` |

### 9.3 Probar el bloqueo geográfico

Usa una VPN con IP de otro país (ej: Estados Unidos) e intenta acceder. Deberías ver:

```
403 Forbidden
Access denied
```

---

## 10. Mantenimiento

### 10.1 Actualizar cloudflared

```bash
# Detener el servicio
systemctl stop cloudflared

# Actualizar
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i cloudflared-linux-amd64.deb

# Iniciar de nuevo
systemctl start cloudflared
```

### 10.2 Ver logs en tiempo real

```bash
journalctl -u cloudflared -f
```

### 10.3 Reiniciar el túnel

```bash
systemctl restart cloudflared
```

### 10.4 Comprobar estado

```bash
cloudflared tunnel info iztack-tomin
```

---

## 📁 Resumen de Archivos de Configuración

| Archivo | Propósito |
|---------|-----------|
| `~/.cloudflared/config.yml` | Configuración del túnel (dominios → servicios) |
| `~/.cloudflared/cert.pem` | Certificado de autenticación con Cloudflare |
| `~/.cloudflared/TU-UUID.json` | Credenciales del túnel |
| `/etc/systemd/system/cloudflared.service` | Servicio del sistema |

---

## 🔒 Checklist de Seguridad

- [ ] Dominio configurado en Cloudflare (nameservers actualizados)
- [ ] Túnel creado y funcionando
- [ ] HTTPS automático (Cloudflare lo maneja)
- [ ] Bloqueo geográfico: solo México
- [ ] Cloudflare Access: autenticación por email
- [ ] WARP instalado en dispositivos autorizados
- [ ] Puerto 22 (SSH) del servidor NO expuesto (solo túnel)
- [ ] Proxmox (`:8006`) NO expuesto (solo red local)

---

> **Nota:** Esta guía usa `tudominio.com` como placeholder. Reemplázalo por tu dominio real (ej: `iztack.com`).
> 
> **Archivos sensibles:** No subas `cert.pem` ni los archivos `.json` de cloudflared a GitHub. Agrégalos a `.gitignore`.