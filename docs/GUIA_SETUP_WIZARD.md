# 🧙 Guía del Setup Wizard — Iztack-Finance

> Configura tu tenant paso a paso, sin editar archivos a mano.

**Última actualización**: 22/06/2026

---

## 🎯 ¿Qué hace?

El wizard te guía para configurar las 3 integraciones que el bot necesita para funcionar:

1. **Telegram** — Token del bot (para enviar/recibir mensajes)
2. **Google Gemini** — API Key (para OCR y entender tickets)
3. **Google APIs (Gmail + Drive)** — OAuth (para guardar facturas y revisar tu correo)

Al terminar:
- ✅ Tus credenciales quedan **cifradas** en la base de datos (AES-256-GCM)
- ✅ Se actualiza el archivo `.env` con las nuevas credenciales
- ✅ El bot de Telegram se **reinicia automáticamente** con el nuevo token

---

## 🚀 Cómo usarlo

### Opción 1: Si acabas de instalar

Entra a `https://finance.iztack.com/setup` (o `http://localhost:3000/setup` si estás en LAN).

### Opción 2: Si quieres reconfigurar

1. Detén los contenedores: `ssh proxmox "cd /opt/iztack-finance && docker compose stop"`
2. Borra la fila del tenant: `ssh proxmox "pct exec 101 -- docker exec sf-postgres psql -U postgres -d sistema_financiero -c 'DELETE FROM tenants;'"`
3. Vuelve a entrar a `/setup`

---

## 📝 Paso a paso

### Paso 1: Telegram Bot Token

**¿Cómo consigo esto?**

1. Abre Telegram
2. Busca `@BotFather`
3. Manda `/newbot`
4. Sigue las instrucciones (nombre, username)
5. BotFather te responde con un token tipo: `1234567890:AAEhBO3eP8dB4xKb5lN6m7o8p9q0r1s2t3u4v`

**En el wizard:**

1. Pega el token
2. Click **Validar**
3. Si todo OK, ves ✅ "Conectado al bot @TuBotName"
4. Click **Siguiente**

### Paso 2: Google Gemini API Key

**¿Cómo consigo esto?**

1. Ve a https://aistudio.google.com/app/apikey
2. Click **Create API key**
3. Selecciona o crea un proyecto de Google Cloud
4. Copia la API key (empieza con `AIzaSy...`)

**En el wizard:**

1. Pega la API key
2. Click **Validar**
3. Si todo OK, ves ✅ "API key válida (modelos Gemini accesibles)"
4. Click **Siguiente**

### Paso 3: Google APIs (Gmail + Drive)

Esta es la parte más complicada. Necesitas 3 cosas:

1. **`client_id`**: Identificador OAuth público
2. **`client_secret`**: Secreto OAuth (NO compartir)
3. **`refresh_token`**: Token de larga duración

**¿Cómo consigo esto?**

1. Ve a https://console.cloud.google.com/apis/credentials
2. Crea un proyecto (si no tienes)
3. Habilita las APIs:
   - **Gmail API** (para buscar facturas en tu correo)
   - **Google Drive API** (para guardar PDFs)
4. Crea credenciales → **OAuth Client ID** → tipo **Desktop app**
5. Te da `client_id` y `client_secret`
6. Para obtener el `refresh_token`, usa esta herramienta:
   ```bash
   pip install google-auth-oauthlib
   ```
   Y sigue el flujo OAuth con scope `https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/drive.file`
   ([tutorial completo](https://developers.google.com/identity/protocols/oauth2/web-server#offline))

**En el wizard:**

1. Pega en este formato (separado por `|`):
   ```
   <client_id>|<client_secret>|<refresh_token>
   ```
2. Click **Validar**
3. Si todo OK, ves ✅ "Refresh token válido (Google OAuth funciona)"
4. Click **Siguiente**

### Paso 4: Confirmar

Revisa el resumen. Si todo se ve bien, click **Guardar y arrancar el bot**.

---

## 🔍 Endpoints del backend

| Endpoint | Método | Para qué |
|---|---|---|
| `/api/setup/status` | `GET` | ¿Ya se completó el setup? (para redirigir al dashboard si sí) |
| `/api/setup/validate` | `POST` | Valida una credencial sin guardarla |
| `/api/setup/finalize` | `POST` | Guarda todo, cifra secretos, reinicia bot |

### Ejemplo: validar Telegram desde curl

```bash
curl -X POST https://api.iztack.com/api/setup/validate \
  -H "Content-Type: application/json" \
  -d '{"provider":"telegram","value":"1234567890:AAEhB..."}'
```

Respuesta:
```json
{
  "valid": true,
  "message": "Conectado al bot @MiBotFinanciero."
}
```

---

## 🛡️ Seguridad

### ¿Cómo se guardan mis secretos?

```
┌──────────────┐      AES-256-GCM       ┌──────────────────┐
│ .env (plano) │  ← al arrancar bot   │   tenants table  │
│              │                        │ (encrypted blob) │
└──────────────┘                        └──────────────────┘
```

- **AES-256-GCM** = estándar militar, 256 bits de entropía
- La clave maestra se genera aleatoriamente y se guarda en `/opt/iztack-finance/.setup_key` con permisos `0600`
- Cada secreto tiene un nonce único de 96 bits
- El `key_id` permite rotar la clave sin perder datos

### ¿Qué pasa si reinicio el contenedor?

El bot lee `.env`, no la DB. El `.env` se actualiza automáticamente al finalizar el setup. Así que **aunque borres la DB, el bot sigue funcionando con `.env`**.

### ¿Qué pasa si reinicio Proxmox?

La clave maestra está en `/opt/iztack-finance/.setup_key` que está bind-mounted. **No se pierde.**

---

## 🧯 Troubleshooting

### "El token no parece válido"

El formato debe ser exacto: `<números>:<letras-y-números>`. Si copiaste mal un carácter, falla.

### "La API key fue rechazada por Google Gemini"

Verifica que:
1. La API key empieza con `AIzaSy`
2. El proyecto tiene habilitada la **Generative Language API**
3. No estás en una región restringida

### "Google OAuth rechazó el token"

El `refresh_token` puede haber expirado (raro) o no tiene los scopes correctos. Vuelve a generarlo con:
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/drive.file`

### "El bot no se reinició"

El endpoint `/finalize` intenta `docker compose restart telegram-bot` desde el contenedor del backend. Si el backend no tiene acceso al socket de Docker, falla silenciosamente. En ese caso, reinicia manualmente:

```bash
ssh proxmox "pct exec 101 -- cd /opt/iztack-finance && docker compose restart telegram-bot"
```

---

## 🔗 Ver también

- `docs/GUIA_ACCESO_REMOTO.md` — Cómo entrar al Proxmox desde fuera
- `docs/ARQUITECTURA_FINAL_v2.md` — Arquitectura del sistema