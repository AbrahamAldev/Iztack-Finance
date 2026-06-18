# 🏗️ Infraestructura de Despliegue

## 📋 Estrategia General

```
┌─────────────────────────────────────────────────────────────────┐
│                        GITHUB (main)                            │
│   git push → GitHub Actions → Tests → Build → Deploy            │
└──────────┬────────────────────────────────────┬─────────────────┘
           │                                    │
           ▼                                    ▼
┌──────────────────────┐          ┌──────────────────────────┐
│  🖥️ Mini PC Local    │          │  ☁️ Hostinger VPS        │
│  (Proxmox LXC)       │          │  (Producción)            │
│                      │          │                          │
│  - Dev/Staging       │          │  - Producción            │
│  - Pruebas con DB    │          │  - Datos reales          │
│    de prueba         │          │  - SSL/HTTPS             │
│  - Branch testing    │          │  - Backup automático     │
│  - Datos anónimos    │          │                          │
└──────────────────────┘          └──────────────────────────┘
```

## 🖥️ Opción Recomendada: Mini PC con Proxmox

### ✅ Por qué Proxmox es perfecto para esto:

| Ventaja | Explicación |
|---------|-------------|
| **LXC (Linux Containers)** | Más ligero que VMs, corre directamente en el kernel |
| **Snapshot antes de actualizar** | Si algo se rompe, vuelves atrás en 1 segundo |
| **Aislamiento** | Cada service en su propio container |
| **Backup integrado** | Backup automático a disco externo/NAS |
| **Bajo consumo** | Una mini PC consume ~15-30W |
| **Docker dentro de LXC** | Perfecto para nuestro docker-compose |

### ❌ No necesitas instalar otro SO
Proxmox ya está basado en **Debian**. Los containers LXC usan el kernel de Proxmox directamente, así que **NO necesitas instalar otro sistema operativo base**.

Simplemente creas containers LXC y dentro corres Docker.

### 🏗️ Estructura recomendada en Proxmox

```
Proxmox VE
├── CT 100: Docker Host (Ubuntu 22.04 LXC)
│   ├── docker-compose (todo el stack)
│   ├── postgres:16
│   ├── redis:7
│   ├── backend:8000
│   ├── frontend:3000
│   └── celery-worker
│
├── CT 101: Base de datos de prueba (PostgreSQL separado)
│   └── Solamente para pruebas de branches
│
├── CT 102: Nginx Proxy Manager (opcional)
│   └── Para manejar dominios y SSL
│
└── Backup semanal automático a disco USB
```

### 📦 Especificación recomendada de Mini PC

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **CPU** | Intel Celeron N5095 | Intel N100 / i3-12100 |
| **RAM** | 8GB | 16GB |
| **Storage** | 256GB SSD | 512GB NVMe + 1TB HDD backups |
| **Modelos** | Beelink U59, Minisforum GK41 | Beelink Ser5, Minisforum TH50 |
| **Consumo** | ~15W | ~25W |
| **Precio** | ~$2,500 MXN | ~$5,000 MXN |

---

## 🔄 Flujo de Trabajo con Git + GitHub

### 🌳 Estrategia de Branches

```
main (producción)
  │
  ├── develop (staging en mini PC)
  │     │
  │     ├── feature/mejora-ocr        ← Nuevas features
  │     ├── feature/nuevo-portal      ← Nuevos portales
  │     ├── fix/error-en-drive        ← Bug fixes
  │     └── experimento/grafana       ← Experimentos
  │
  └── hotfix/critical-bug             ← Urgente, va directo a main
```

### 🔄 Flujo Completo

```
1. git checkout -b feature/nuevo-portal
2. 👨‍💻 Hacer cambios en el código
3. git push origin feature/nuevo-portal
4. 🤖 GitHub Actions corre TESTS automáticos
5. 🔄 Si hay tests → CI/CD deploya a MINI PC (staging)
6. 🧪 Probar en mini PC con DB de prueba
7. ✅ Si funciona → Crear Pull Request a develop
8. 🔄 GitHub Actions deploya develop a MINI PC
9. 🧪 Pruebas finales en mini PC
10. 🚀 Pull Request a main → CI/CD deploys a HOSTINGER
```

### 🤖 GitHub Actions Automatiza:

| Evento | Acción |
|--------|--------|
| `push a feature/*` | Tests unitarios + lint |
| `push a develop` | Tests → Build → Deploy a mini PC |
| `push a main` | Tests → Build → Deploy a Hostinger |
| `Pull Request` | Tests obligatorios antes de mergear |
| `tag v*.*.*` | Deploy con versión específica |

---

## 🚀 Setup Paso a Paso

### 1. GitHub

```bash
cd /Users/abraham/Documents/Cursor/Sistema\ financiero

# Crear el repositorio en GitHub primero (desde web)

# Conectar local con GitHub
git remote add origin https://github.com/TU_USUARIO/sistema-financiero.git
git branch -M main
git push -u origin main

# Crear develop branch
git checkout -b develop
git push -u origin develop
```

### 2. Mini PC (Proxmox)

#### 2.1 Crear container LXC

```bash
# Desde la shell de Proxmox:
pct create 100 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname docker-host \
  --storage local-lvm \
  --rootfs 20 \
  --cores 4 \
  --memory 4096 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --unprivileged 1 \
  --features nesting=1

# Iniciar container
pct start 100

# Entrar al container
pct enter 100
```

#### 2.2 Instalar Docker dentro del LXC

```bash
# Dentro del container LXC:
apt update && apt upgrade -y
apt install -y curl ca-certificates

# Docker
curl -fsSL https://get.docker.com | sh
usermod -aG docker root

# Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verificar
docker --version
docker-compose --version
```

#### 2.3 Clonar y desplegar en mini PC

```bash
# Dentro del container LXC:
mkdir -p /opt/sistema-financiero
cd /opt/sistema-financiero

# Clonar (branch develop para staging)
git clone -b develop https://github.com/TU_USUARIO/sistema-financiero.git .
cp .env.example .env
nano .env  # Configurar API keys de prueba

# Iniciar
docker-compose up -d

# Verificar
docker-compose ps
```

### 3. Hostinger VPS (Producción)

#### 3.1 Setup inicial en Hostinger

```bash
# SSH al VPS
ssh root@TU_IP_HOSTINGER

# Actualizar
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com | sh

# Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Crear estructura
mkdir -p /opt/sistema-financiero
cd /opt/sistema-financiero
```

#### 3.2 Nginx Reverse Proxy (SSL)

```bash
# Instalar Nginx
apt install -y nginx certbot python3-certbot-nginx

# Configurar dominio
cat > /etc/nginx/sites-available/sistema-financiero << 'EOF'
server {
    listen 80;
    server_name tudominio.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Habilitar sitio
ln -s /etc/nginx/sites-available/sistema-financiero /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# SSL con Let's Encrypt
certbot --nginx -d tudominio.com
```

---

## 🤖 GitHub Actions

Los workflows se crearán automáticamente al hacer push. Pero primero hay que configurar los **SECRETS** en GitHub:

### Secrets necesarios en GitHub

Ve a: `GitHub → Settings → Secrets and variables → Actions`

| Secret | Descripción | Dónde obtenerlo |
|--------|-------------|-----------------|
| `HOSTINGER_SSH_KEY` | Llave privada SSH | `ssh-keygen -t ed25519` |
| `HOSTINGER_HOST` | IP del VPS | Hostinger dashboard |
| `MINIPC_SSH_KEY` | Llave privada para mini PC | `ssh-keygen` en mini PC |
| `MINIPC_HOST` | IP local de mini PC | `ip a` en mini PC |
| `GEMINI_API_KEY` | API key de Gemini | Google AI Studio |
| `TELEGRAM_BOT_TOKEN` | Token de bot | @BotFather |
| `GOOGLE_CLIENT_ID` | OAuth Client ID | Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | OAuth Secret | Google Cloud Console |
| `GOOGLE_REFRESH_TOKEN` | Refresh token | Script de autenticación |
| `SECRET_KEY` | Clave maestra cifrado | `openssl rand -hex 32` |

### Cómo generar SSH keys para GitHub Actions

```bash
# En tu Mac:
ssh-keygen -t ed25519 -f ~/.ssh/github-actions -C "github-actions"

# Agregar la llave pública a los servidores:
# En mini PC:
ssh-copy-id -i ~/.ssh/github-actions.pub root@MINIPC_IP
# En Hostinger:
ssh-copy-id -i ~/.ssh/github-actions.pub root@HOSTINGER_IP

# Agregar la PRIVADA a GitHub Secrets:
cat ~/.ssh/github-actions
# Copiar todo el contenido como HOSTINGER_SSH_KEY
```

---

## 🧪 Base de Datos de Prueba

Para probar branches sin afectar datos reales, usa una DB separada:

```yaml
# docker-compose.test.yml (archivo separado para pruebas)
version: '3.8'

services:
  postgres-test:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: sistema_financiero_test
    ports:
      - "5433:5432"  # Puerto diferente para no conflictos
    volumes:
      - postgres_test_data:/var/lib/postgresql/data

  backend-test:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://test:test@postgres-test:5432/sistema_financiero_test
      ENVIRONMENT: testing
    # ... resto igual

volumes:
  postgres_test_data:
```

```bash
# Correr pruebas localmente
docker-compose -f docker-compose.test.yml up -d
```

---

## 📦 Backup Automático

### En Proxmox (backup semanal automático)

```
Datacenter → Backup → Add
  - Storage: local (o NAS)
  - Schedule: Sun 02:00
  - Compression: ZSTD
  - Mode: Snapshot
```

### Backup de la base de datos (diario)

```bash
# En el container LXC, crear cron:
crontab -e

# Agregar:
0 3 * * * docker exec sf-postgres pg_dump -U postgres sistema_financiero | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz
0 4 * * * find /backups -name "*.sql.gz" -mtime +30 -delete
```

---

## 📊 Costos Mensuales Estimados

| Servicio | Costo |
|----------|-------|
| **Mini PC** (1-time) | ~$3,000-5,000 MXN |
| **Electricidad** (25W 24/7) | ~$50 MXN/mes |
| **Hostinger VPS** | ~$150 MXN/mes |
| **Gemini API** (gratis) | $0 (60 requests/minuto gratis) |
| **Google APIs** (gratis) | $0 (límites generosos) |
| **GitHub** (gratis) | $0 |
| **Total mensual** | **~$200 MXN/mes** |

---

## 🔧 Troubleshooting

### Problema: No puedo ejecutar Docker dentro de LXC
**Solución:** Asegúrate de que el container tenga `nesting=1`:
```bash
pct set 100 --features nesting=1
```

### Problema: La mini PC no tiene suficiente RAM
**Solución:** Reduce los recursos de Docker:
```yaml
# En docker-compose.yml, limitar servicios:
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
```

### Problema: Quiero acceder al dashboard desde fuera de casa
**Solución:** Usa Cloudflare Tunnel (gratis) o configura port forwarding en tu router:
```bash
# Opción 1: Cloudflare Tunnel (recomendado, más seguro)
# Opción 2: Port forwarding en router + DDNS (no-pi.com)