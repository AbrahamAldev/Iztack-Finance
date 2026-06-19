# 🚀 Guía de Despliegue Paso a Paso — Iztack-Tomin

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
Repository name: Iztack-Tomin
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
cd /Users/abraham/Documents/Cursor/Iztack-Tomin

# Decirle a Git que se conecte con GitHub (REEMPLAZA "TU_USUARIO" por tu nombre de GitHub)
git remote add origin git@github.com:TU_USUARIO/Iztack-Tomin.git

# Subir la rama principal
git push -u origin main
```

Si te pide confirmación (`"Are you sure you want to continue connecting?"`), escribe `yes` y Enter.

✅ **¡Código subido a GitHub!** Puedes verificarlo yendo a:
`https://github.com/TU_USUARIO/Iztack-Tomin`

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

# PARTE 3: CREAR EL CONTENEDOR Y DESPLEGAR

## Paso 1: Abrir la terminal de Proxmox

1. En la interfaz web de Proxmox
2. Selecciona el nodo (el nombre de tu servidor)
3. Haz clic en **">_ Shell"** en la parte superior
4. ✅ Terminal abierta

## Paso 2: Crear el contenedor LXC

Copia y pega **exactamente** este comando completo (todas las líneas juntas):

```bash
pct create 100 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname iztack-tomin \
  --storage local-lvm \
  --rootfs 20 \
  --cores 4 \
  --memory 4096 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --unprivileged 1 \
  --features nesting=1
```

**Explicación de cada parte:**
- `pct create 100` → Crea un contenedor con ID 100
- `ubuntu-22.04-standard` → Usa Ubuntu 22.04 (sistema operativo base)
- `--hostname iztack-tomin` → El nombre del contenedor
- `--rootfs 20` → 20 GB de disco
- `--cores 4` → 4 núcleos de CPU
- `--memory 4096` → 4 GB de RAM
- `ip=dhcp` → Obtiene IP automáticamente
- `features nesting=1` → Permite ejecutar Docker dentro del contenedor

## Paso 3: Iniciar el contenedor

```bash
pct start 100
```

## Paso 4: Entrar al contenedor

```bash
pct enter 100
```

Ahora tu terminal está DENTRO del contenedor. Lo sabrás porque el prompt cambia a algo como `root@iztack-tomin:~#`

## Paso 5: Instalar Docker dentro del contenedor

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

## Paso 6: Clonar el proyecto desde GitHub

```bash
# Ir a la carpeta donde se instalará el sistema
cd /opt

# Clonar el proyecto (REEMPLAZA "TU_USUARIO" por tu nombre de GitHub)
git clone -b develop https://github.com/TU_USUARIO/Iztack-Tomin.git iztack-tomin

# Entrar a la carpeta
cd iztack-tomin
```

## Paso 7: Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Abrir el archivo para editarlo
nano .env
```

Se abrirá un editor dentro de la terminal. **Pega esto** (presiona Cmd+V o haz clic derecho → Pegar):

```
SECRET_KEY=pon-aqui-una-clave-segura
TELEGRAM_BOT_TOKEN=pon-aqui-el-token-de-tu-bot
GEMINI_API_KEY=pon-aqui-tu-api-key-de-gemini
```

- **SECRET_KEY**: puedes poner cualquier texto largo, ej: `mi-clave-super-segura-12345`
- **TELEGRAM_BOT_TOKEN**: lo obtienes de @BotFather en Telegram
- **GEMINI_API_KEY**: la obtienes de https://aistudio.google.com

Para guardar los cambios en nano:
1. Presiona `Ctrl + X` (Control + X)
2. Presiona `Y` (Yes)
3. Presiona `Enter`

## Paso 8: Desplegar el sistema

```bash
# Iniciar todos los servicios
docker-compose up -d

# Verificar que están corriendo
docker-compose ps
```

Deberías ver 6 servicios con estado "Up":
- postgres
- redis
- caddy
- api
- worker
- adminer

## Paso 9: Obtener la IP del contenedor

```bash
# Salir del contenedor (presiona Ctrl + D)
exit

# Ver la IP del contenedor
pct enter 100 -- ip a | grep eth0
```

Anota la dirección IP (algo como `192.168.1.101`)

## Paso 10: ¡Probar que funciona!

Desde tu Mac (o cualquier dispositivo en la misma red):

1. Abre el navegador
2. Prueba el backend: `http://192.168.1.101:8000/api/health`
   - Deberías ver: `{"status": "healthy", "app": "Iztack-Tomin", ...}`
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
5. Responde: **"IztackTominBot"**
6. Responde: **"Iztack_Tomin_Bot"** (debe terminar en "bot")
7. @BotFather te dará un **TOKEN**. Se ve así: `7234567890:AAHdqTcvCH1vGWJxfSeOfS0se`
8. **COPIA ESE TOKEN INMEDIATAMENTE** (no lo pierdas, después no lo podrás ver de nuevo)

## 4.2 Agregar el token al sistema

```bash
# Entrar al contenedor
pct enter 100

# Ir a la carpeta del proyecto
cd /opt/iztack-tomin

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

1. Busca tu bot en Telegram: **@Iztack_Tomin_Bot**
2. Envía: `/start`
3. Envía una **foto de un ticket** de cualquier tienda
4. El bot procesará el ticket y te responderá

---

# PARTE 5: FLUJO DE TRABAJO DIARIO

## Cuando quieras hacer cambios

```bash
# En tu Mac:
cd /Users/abraham/Documents/Cursor/Iztack-Tomin

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