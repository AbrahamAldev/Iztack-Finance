# 🚀 Guía de Despliegue Paso a Paso — Iztack-Finance

## Para principiantes absolutos

Esta guía te explica **con lujo de detalles** cómo subir el proyecto a GitHub, configurar Proxmox, y desplegar el sistema. No necesitas experiencia previa.

---

# PARTE 1: SUBIR EL CÓDIGO A GITHUB

## ¿Qué es GitHub?

GitHub es como un **Google Drive para código**. Guarda tu proyecto en la nube y permite:
- Tener control de versiones (historial de cambios)
- Que el código se deploye automáticamente a tus servidores
- Compartir el proyecto con otras personas

## Paso 1: Crear una cuenta en GitHub

1. Abre tu navegador (Chrome, Safari, Edge)
2. Ve a: **https://github.com**
3. Haz clic en el botón verde **"Sign up"** (Registrarse)
4. Llena el formulario:
   - **Email**: tu correo electrónico
   - **Password**: una contraseña segura (guárdala en tu gestor de contraseñas)
   - **Username**: elige un nombre de usuario (ej: `abraham` o `tunombre`)
5. Verifica tu correo (te llegará un email de GitHub)
6. ¡Listo! Ya tienes cuenta

## Paso 2: Crear el repositorio en GitHub

1. Inicia sesión en **github.com**
2. Verás un botón verde **"+ New"** en la esquina superior derecha (al lado de tu foto de perfil)
3. O haz clic aquí directo: https://github.com/new
4. Llena:

```
Repository name: Iztack-Finance
Description (opcional): Sistema de control de finanzas personales y PyMEs
Private / Public: PRIVATE (marca Private)
```

5. **NO** marques "Initialize this repository with a README" (ya tenemos uno)
6. Haz clic en el botón verde **"Create repository"**

✅ **¡Repositorio creado!**

## Paso 3: Conectar tu Mac con GitHub por SSH (una sola vez)

Esto permite que tu Mac hable con GitHub sin pedir contraseña cada vez.

### 3.1 Abrir la Terminal

1. Presiona `Cmd + Espacio` (tecla Comando + barra espaciadora)
2. Escribe **"Terminal"** y presiona Enter
3. Se abrirá una ventana blanca/negra

### 3.2 Generar una llave SSH

Copia y pega **exactamente** este comando en la Terminal y presiona Enter:

```bash
ssh-keygen -t ed25519 -C "tu-correo@ejemplo.com"
```

**Reemplaza** `tu-correo@ejemplo.com` por el correo que usaste en GitHub.

- Te preguntará: `"Enter file in which to save the key"` → Presiona **Enter** (sin escribir nada, usa el default)
- Te preguntará: `"Enter passphrase"` → Presiona **Enter** (vacío)
- Te preguntará: `"Enter same passphrase again"` → Presiona **Enter**
- ✅ Llave generada

### 3.3 Agregar la llave a GitHub

Pega **exactamente** este comando:

```bash
cat ~/.ssh/id_ed25519.pub
```

Verás algo como:
```
ssh-ed25519 AAAAC3... mucho texto... tu-correo@ejemplo.com
```

1. **Selecciona todo ese texto** con el mouse
2. Presiona `Cmd + C` para copiarlo
3. Ve a GitHub: **Settings → SSH and GPG keys**
   - URL directa: https://github.com/settings/keys
4. Haz clic en **"New SSH key"**
5. Ponle un nombre: **"Mi Mac"**
6. **Pega** (Cmd + V) el texto que copiaste
7. Haz clic en **"Add SSH key"**
8. ✅ Llave agregada

## Paso 4: Subir el proyecto a GitHub

Ahora pega **estos comandos UNO POR UNO** en la Terminal, presionando Enter después de cada línea:

```bash
# Ir a la carpeta del proyecto
cd /Users/abraham/Documents/Cursor/Iztack-Finance

# Decirle a Git que se conecte con GitHub (REEMPLAZA "TU_USUARIO" por tu nombre de GitHub)
git remote add origin git@github.com:TU_USUARIO/Iztack-Finance.git

# Subir la rama principal
git push -u origin main
```

Si te pide confirmación (`"Are you sure you want to continue connecting?"`), escribe `yes` y Enter.

✅ **¡Código subido a GitHub!** Puedes verificarlo yendo a:
`https://github.com/TU_USUARIO/Iztack-Finance`

## Paso 5: Crear la rama develop

Pega este comando:

```bash
git checkout -b develop && git push -u origin develop
```

Ahora tienes dos "ramas" (versiones) del proyecto:
- `main` → la versión estable (producción)
- `develop` → la versión de pruebas (staging)

---

# PARTE 2: ACTUALIZAR PROXMOX

## ¿Qué es Proxmox?

Proxmox es un sistema operativo para servidores que permite crear "contenedores" (como mini computadoras virtuales). Tu mini PC ya lo tiene instalado.

## Paso 1: Acceder a Proxmox

1. Desde **cualquier computadora en tu red local** (puede ser tu Mac o un celular)
2. Abre el navegador
3. Escribe en la barra de direcciones: `https://192.168.1.100:8006`
   - (Si no sabes la IP, busca en tu router "dispositivos conectados" y busca el nombre de tu mini PC)
4. Te aparecerá una advertencia de seguridad → Haz clic en **"Advanced"** → **"Proceed to 192.168.1.100"**
5. Inicia sesión con:
   - **User**: `root`
   - **Password**: la contraseña que pusiste al instalar Proxmox

## Paso 2: Actualizar Proxmox

Una vez dentro de la interfaz web de Proxmox:

### Opción A: Desde la interfaz web (recomendado)

1. A la izquierda, selecciona el nodo (el nombre de tu servidor, ej: `pve`)
2. Haz clic en el botón **"Updates"** (o "Actualizaciones") en el menú de arriba
3. Haz clic en **"Refresh"** (Actualizar lista de paquetes)
4. Haz clic en **"Upgrade"** → Confirma
5. Espera a que termine (puede tardar 2-5 minutos)

### Opción B: Desde la terminal de Proxmox (más rápido)

1. En la interfaz web de Proxmox, a la izquierda, selecciona el nodo
2. Haz clic en el botón **">_ Shell"** en la parte superior
3. Se abrirá una terminal NEGRA dentro de la página web

Pega estos comandos UNO POR UNO (presiona Enter después de cada uno):

```bash
# Actualizar las listas de paquetes
apt update

# Actualizar los paquetes instalados
apt upgrade -y

# Actualizar el kernel de Proxmox
pve6x-upgrade  # Solo si estás en Proxmox 6.x

# Limpiar paquetes viejos
apt autoremove -y
```

4. Cuando termine, **reiniciamos**:

```bash
reboot
```

5. Espera 2 minutos y recarga la página web de Proxmox

✅ **Proxmox actualizado**

---

# PARTE 3: CONFIGURAR LOS DISCOS DE ALMACENAMIENTO (RECOMENDADO)

> **⚠️ IMPORTANTE:** Esta sección es **opcional**. Iztack-Finance funciona perfectamente con un solo disco SSD. La configuración de múltiples discos es una **recomendación** para que tu servidor casero pueda soportar mejor servicios adicionales en el futuro:
> 
> | Disco | Propósito |
> |-------|-----------|
> | **SSD** (cualquier capacidad) | Sistema Proxmox + contenedores (rápido) → **MÍNIMO REQUERIDO** |
> | **HDD 1TB** | Datos fríos de contenedores → **RECOMENDADO** |
> | **HDD 2TB (exFAT)** | NAS portátil para transportar archivos → **OPCIONAL** |
>
> Si solo tienes un SSD, puedes **saltar directo al [Paso 6](#paso-6-crear-el-contenedor-lxc)**.

Antes de crear el contenedor, así organizamos los discos en este servidor:

```
┌─────────────────────────────────────────────────────────┐
│                ARQUITECTURA DE ALMACENAMIENTO            │
├──────────────┬──────────┬───────────────────────────────┤
│    DISCO     │ TAMAÑO   │            USO                │
├──────────────┼──────────┼───────────────────────────────┤
│ SSD          │ Cualquier│ Sistema Proxmox + raíz de CTs │
│ HDD (opc)    │ 1 TB     │ Datos fríos para contenedores │
│ HDD (opc)    │ 2 TB     │ NAS portátil (exFAT)          │
└──────────────┴──────────┴───────────────────────────────┘
```

> **Nota:** Los nombres de los discos (sda, sdb, sdc) varían según tu hardware. Usa `lsblk` para identificar los tuyos.

## Paso 1: Abrir la terminal de Proxmox

1. En la interfaz web de Proxmox
2. Selecciona el nodo (el nombre de tu servidor)
3. Haz clic en **">_ Shell"** en la parte superior
4. ✅ Terminal abierta

## Paso 2: Identificar los discos disponibles

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE | grep -v loop
```

Identifica:
- **SSD del sistema** → donde está instalado Proxmox (suele ser el más pequeño, ej: 128GB)
- **Disco para NAS portátil** → el que quieras formatear como exFAT (compatible Windows/Mac)
- **Disco para datos fríos** → el que usarán los contenedores para almacenamiento masivo

## Paso 3: Formatear el disco NAS portátil (exFAT)

> **⚠️ ADVERTENCIA:** Esto BORRA todos los datos del disco seleccionado.

Elige el disco que será tu NAS portátil (ej: `/dev/sdb`). Ejecuta:

```bash
# Reemplaza /dev/sdb por el disco que elegiste para NAS
parted /dev/sdb mklabel gpt
parted /dev/sdb mkpart primary 0% 100%
mkfs.exfat /dev/sdb1
```

Este disco será compatible con Windows, macOS y Linux. Puedes desconectarlo y llevarlo a cualquier computadora.

## Paso 4: Preparar el disco de datos fríos (ext4)

Elige el disco que será para datos fríos (ej: `/dev/sdc`). Ejecuta:

```bash
# Limpiar firmas de sistemas de archivos anteriores (si el disco se usó antes)
wipefs -a /dev/sdc1

# Formatear como ext4
mkfs.ext4 /dev/sdc1

# Crear punto de montaje
mkdir -p /mnt/NOMBRE_DEL_STORAGE

# Montar el disco
mount /dev/sdc1 /mnt/NOMBRE_DEL_STORAGE

# Verificar
df -h /mnt/NOMBRE_DEL_STORAGE
```

**Reemplaza:**
- `/dev/sdc1` → por tu disco real
- `NOMBRE_DEL_STORAGE` → por el nombre que quieras (ej: `datos-frios`, `storage`, `data`)

## Paso 5: Dar de alta el storage en Proxmox

Para que los contenedores puedan usar el disco de datos fríos fácilmente:

```bash
pvesm add dir NOMBRE_DEL_STORAGE --path /mnt/NOMBRE_DEL_STORAGE --content rootdir,images,vztmpl
```

Verifica que aparezca:

```bash
pvesm status
```

## Paso 6: Crear el contenedor LXC

Ahora creamos el contenedor donde correrá Iztack-Finance. El disco raíz va en el **SSD** (rápido) y el disco de datos fríos se monta dentro usando `--mp0`.

```bash
# Descargar template de Ubuntu 22.04 (si no lo tienes)
pveam update
pveam download local ubuntu-22.04-standard_22.04-1_amd64.tar.zst

# Crear contenedor (cambia el ID si el 100 ya está ocupado, usa pct list para ver IDs libres)
pct create 100 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname iztack-finance \
  --storage local-lvm \
  --rootfs 8 \
  --cores 2 \
  --memory 2048 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --unprivileged 1 \
  --features nesting=1 \
  --mp0 /mnt/NOMBRE_DEL_STORAGE,mp=/mnt/data
```

**Explicación de cada parte:**
- `pct create 100` → Crea un contenedor con ID 100 (usa otro número si está ocupado)
- `ubuntu-22.04-standard` → Usa Ubuntu 22.04 (sistema operativo base)
- `--storage local-lvm` → El disco raíz va en el SSD (más rápido)
- `--rootfs 8` → 8 GB para el sistema operativo
- `--cores 2` → 2 núcleos de CPU
- `--memory 2048` → 2 GB de RAM
- `ip=dhcp` → Obtiene IP automáticamente
- `features nesting=1` → Permite ejecutar Docker dentro del contenedor
- `--mp0 /mnt/NOMBRE_DEL_STORAGE,mp=/mnt/data` → Monta el disco de datos fríos dentro del contenedor en `/mnt/data`

## Paso 7: Iniciar el contenedor

```bash
pct start 100
```

## Paso 8: Entrar al contenedor

```bash
pct enter 100
```

Ahora tu terminal está DENTRO del contenedor. Lo sabrás porque el prompt cambia a algo como `root@iztack-finance:~#`

## Paso 9: Instalar Docker dentro del contenedor

Copia y pega **todo esto de una sola vez** (son 3 comandos seguidos):

```bash
# Actualizar paquetes
apt update && apt upgrade -y

# Instalar dependencias
apt install -y curl ca-certificates git

# Instalar Docker
curl -fsSL https://get.docker.com | sh

# Verificar que Docker se instaló
docker --version
```

Deberías ver algo como: `Docker version 24.0.7, build afdd53b`

> **Nota sobre el mensaje de Docker:** Si ves un mensaje como `To run Docker as a non-privileged user...` o `WARNING: Access to the remote API...` — **no es un error**. Es solo una advertencia de Docker diciendo que puedes ejecutarlo como usuario normal (no root). Docker ya quedó instalado correctamente. Puedes ignorar este mensaje y continuar.

## Paso 10: Clonar el proyecto desde GitHub

```bash
# Ir a la carpeta donde se instalará el sistema
cd /opt

# Clonar el proyecto (REEMPLAZA "TU_USUARIO" por tu nombre de GitHub)
git clone -b develop https://github.com/TU_USUARIO/Iztack-Finance.git iztack-finance

# Entrar a la carpeta
cd iztack-finance
```

> **¿Cómo obtener un Personal Access Token?**
> 
> Cuando ejecutes `git clone`, te pedirá:
> - **Username**: tu nombre de usuario de GitHub (ej: `juanperez`)
> - **Password**: NO es tu contraseña de GitHub. Debes usar un **Personal Access Token**.
>
> Para generar el token:
> 1. Ve a **GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)**
>    - URL directa: https://github.com/settings/tokens
> 2. Haz clic en **"Generate new token (classic)"**
> 3. Dale un nombre: **"Iztack-Finance Deploy"**
> 4. Marca estos permisos:
>    - [x] `repo` (acceso completo a repositorios)
> 5. Haz clic en **"Generate token"**
> 6. **COPIA EL TOKEN INMEDIATAMENTE** (se ve así: `ghp_xxxxxxxxxxxxxxxxxxxx`). GitHub no lo mostrará de nuevo.
> 7. Usa ese token como **password** cuando te lo pida el `git clone`.
>
> **Nota:** Cada persona que clone el repositorio debe usar **su propio usuario y su propio token**. No uses los míos.

## Paso 11: Instalar Docker Compose (si no está instalado)

```bash
# Verificar si docker-compose existe
docker compose version
```

Si ves `Docker Compose version v2...` → ya está instalado ✅. Usa `docker compose` (sin guión) en lugar de `docker-compose`.

Si no está instalado:
```bash
apt install -y docker-compose-plugin
```

## Paso 12: Instalar Portainer (opcional - administrador visual de contenedores)

Portainer te permite ver y administrar todos tus contenedores desde una interfaz web en lugar de la terminal.

```bash
# Crear el contenedor de Portainer
docker run -d \
  --name portainer \
  --restart always \
  -p 9000:9000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  portainer/portainer-ce:latest
```

Luego accede desde el navegador: `http://IP_DEL_CONTENEDOR:9000`
- En la primera visita, crea una contraseña de administrador
- Selecciona "Local" como entorno
- ¡Listo! Verás todos tus contenedores con opciones para iniciar, detener, ver logs, etc.

## Paso 13: Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Abrir el archivo para editarlo
nano .env
```

Se abrirá un editor dentro de la terminal. Verás algo como:

```
SECRET_KEY=pon-aqui-una-clave-segura
TELEGRAM_BOT_TOKEN=pon-aqui-el-token-de-tu-bot
GEMINI_API_KEY=pon-aqui-tu-api-key-de-gemini
```

**Reemplaza** los valores de ejemplo con tus datos reales. Si una variable ya tiene un valor de ejemplo y no quieres borrarla, puedes poner `#` al inicio de la línea para comentarla y escribir la tuya debajo:

```
# SECRET_KEY=pon-aqui-una-clave-segura  ← esta línea se ignora por el #
SECRET_KEY=mi-clave-real-super-segura
```

### 🔑 SECRET_KEY

Es la clave maestra para cifrar tus contraseñas de portales CFDI y tokens de nube. 

**Opción 1 — Recomendada (generar una segura):**
```bash
# Este comando genera una clave de 64 caracteres aleatorios
openssl rand -hex 32
```
Copia el resultado y pégalo como valor de `SECRET_KEY`.

**Opción 2 — Rápida (cualquier texto largo):**
```
SECRET_KEY=mi-clave-super-segura-12345-cambiame-en-produccion
```

> **Importante:** Si cambias esta clave después de haber guardado credenciales, las credenciales anteriores quedarán inservibles.

### 🤖 TELEGRAM_BOT_TOKEN

1. Abre Telegram en tu celular o computadora
2. Busca **@BotFather** (es el usuario oficial de Telegram para crear bots, tiene palomita azul)
3. Haz clic en **"Start"** o escribe `/start`
4. Escribe: `/newbot`
5. BotFather te pedirá un nombre para tu bot. Escribe: **IztackFinanceBot**
6. Luego te pedirá un username. Debe terminar en "bot". Escribe: **Iztack_Finance_Bot**
7. BotFather te responderá con algo como:

```
Done! Congratulations on your new bot. You will find it at:
t.me/Iztack_Finance_Bot

Use this token to access the HTTP API:
7234567890:AAHdqTcvCH1vGWJxfSeOfS0se
```

8. **COPIA ESE TOKEN INMEDIATAMENTE** (el número largo con letras y números). Es la única vez que BotFather te lo mostrará.
9. Pégalo en el `.env`:
```
TELEGRAM_BOT_TOKEN=7234567890:AAHdqTcvCH1vGWJxfSeOfS0se
```

> Si pierdes el token, puedes crear uno nuevo con `/newbot` o pedirle a @BotFather que te lo muestre con `/token`.

### 🧠 GEMINI_API_KEY

1. Ve a **https://aistudio.google.com/app/apikey**
2. Inicia sesión con tu cuenta de Google
3. Haz clic en **"Create API Key"** (Crear clave API)
4. Selecciona tu proyecto de Google Cloud (o crea uno nuevo)
5. Copia la clave que te aparece (se ve así: `AIzaSyxxxxxxxxxxxxxxxxxxxxx`)
6. Pégalo en el `.env`:
```
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxx
```

> La clave es **gratuita** para uso personal con límites generosos. No necesitas tarjeta de crédito.

Para guardar los cambios en nano:
1. Presiona `Ctrl + X` (Control + X)
2. Presiona `Y` (Yes)
3. Presiona `Enter`

## Paso 14: Desplegar el sistema

```bash
# Iniciar todos los servicios
docker compose up -d

# Verificar que están corriendo
docker compose ps
```

Deberías ver 7 servicios con estado "Up" (6 de Iztack-Finance + 1 de Portainer):
- postgres
- redis
- caddy
- api
- worker
- adminer
- portainer

> **Nota sobre docker-compose vs docker compose:** En versiones recientes de Docker, el comando `docker-compose` (con guión) fue reemplazado por `docker compose` (sin guión). Si `docker-compose` te da `Command not found`, usa `docker compose`.

## Paso 15: Obtener la IP del contenedor

```bash
# Salir del contenedor (presiona Ctrl + D)
exit

# Ver la IP del contenedor
pct enter 100 -- ip a | grep eth0
```

Anota la dirección IP (algo como `192.168.1.101`)

## Paso 16: ¡Probar que funciona!

Desde tu Mac (o cualquier dispositivo en la misma red):

1. Abre el navegador
2. Prueba el backend: `http://192.168.1.101:8000/api/health`
   - Deberías ver: `{"status": "healthy", "app": "Iztack-Finance", ...}`
3. Prueba el frontend: `http://192.168.1.101:3000`
   - Deberías ver la página principal del dashboard
4. Prueba Adminer: `http://192.168.1.101:8080`
   - Servidor: `postgres`
   - Usuario: `postgres`
   - Contraseña: `postgres`
   - Base de datos: `sistema_finanzas`

✅ **¡Sistema desplegado exitosamente!**

---

# PARTE 4: PROBAR EL BOT DE TELEGRAM

## 4.1 Crear el bot en Telegram

1. Abre Telegram en tu celular
2. Busca **@BotFather** (es un usuario verificado con palomita azul)
3. Haz clic en **"Start"**
4. Escribe: `/newbot`
5. Responde: **"IztackFinanceBot"**
6. Responde: **"Iztack_Finance_Bot"** (debe terminar en "bot")
7. @BotFather te dará un **TOKEN**. Se ve así: `7234567890:AAHdqTcvCH1vGWJxfSeOfS0se`
8. **COPIA ESE TOKEN INMEDIATAMENTE** (no lo pierdas, después no lo podrás ver de nuevo)

## 4.2 Agregar el token al sistema

```bash
# Entrar al contenedor
pct enter 100

# Ir a la carpeta del proyecto
cd /opt/iztack-finance

# Editar el .env
nano .env
```

Busca la línea `TELEGRAM_BOT_TOKEN=` y pon el token que te dio BotFather:
```
TELEGRAM_BOT_TOKEN=7234567890:AAHdqTcvCH1vGWJxfSeOfS0se
```

Guarda con `Ctrl + X` → `Y` → `Enter`

```bash
# Reiniciar el bot para que use el nuevo token
docker-compose restart bot

# Salir del contenedor
exit
```

## 4.3 Usar el bot

1. Busca tu bot en Telegram: **@Iztack_Finance_Bot**
2. Envía: `/start`
3. Envía una **foto de un ticket** de cualquier tienda
4. El bot procesará el ticket y te responderá

---

# PARTE 5: FLUJO DE TRABAJO DIARIO

## Cuando quieras hacer cambios

```bash
# En tu Mac:
cd /Users/abraham/Documents/Cursor/Iztack-Finance

# 1. Crear una rama para tu cambio
git checkout -b feature/mi-mejora

# 2. Hacer cambios en el código...

# 3. Guardar los cambios
git add .
git commit -m "Descripción de lo que hice"

# 4. Subir a GitHub
git push origin feature/mi-mejora
```

✅ **GitHub Actions correrá los tests automáticamente**

## Cuando quieras probar en la Mini PC

```bash
# 5. Unir los cambios a develop
git checkout develop
git merge feature/mi-mejora

# 6. Subir develop
git push origin develop
```

✅ **GitHub Actions deployará automáticamente a tu Mini PC**

## Cuando quieras pasar a producción

```bash
# 7. Unir a main
git checkout main
git merge develop

# 8. Subir main
git push origin main
```

✅ **GitHub Actions deployará a Hostinger con backup automático**

---

# RESOLUCIÓN DE PROBLEMAS COMUNES

### ❌ "Permission denied (publickey)" al hacer git push
➡️ No configuraste SSH correctamente. Repite el Paso 3 de la Parte 1.

### ❌ "docker: command not found"
➡️ Docker no se instaló. Repite desde el Paso 5 de la Parte 3.

### ❌ No puedo acceder a `http://192.168.1.101:8000`
➡️ La IP puede ser diferente. Encuentra la IP real:
```bash
pct enter 100
hostname -I
```

### ❌ El contenedor no inicia
➡️ Puede faltar espacio en disco. En Proxmox:
```bash
pct status 100
pct resize 100 rootfs +10G  # Agregar 10GB más
pct start 100
```

### ❌ No sé qué IP tiene mi Mini PC
➡️ Revisa tu router (en la página de "Dispositivos conectados") o usa:
```bash
# En Proxmox:
ip a
```

### ❌ El bot de Telegram no responde
➡️ Verifica que el token esté bien en `.env` y reinicia:
```bash
docker-compose restart bot
docker-compose logs bot  # Ver errores
```

---

# COMANDOS ÚTILES DE PROXMOX

```bash
# Ver todos los contenedores
pct list

# Ver el estado de un contenedor
pct status 100

# Apagar un contenedor
pct shutdown 100

# Iniciar un contenedor
pct start 100

# Entrar a un contenedor
pct enter 100

# Ver logs del sistema
pct enter 100
journalctl -xe

# Verificar Docker dentro del contenedor
pct enter 100
docker ps

# Ver logs de un servicio específico
docker-compose logs api
docker-compose logs worker
docker-compose logs bot

# Reiniciar un servicio
docker-compose restart api

# Ver uso de recursos
pct enter 100
htop