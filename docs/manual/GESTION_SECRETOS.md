# 🔐 Gestión de Secretos — Buenas Prácticas

> **Principio fundamental:** un secreto NO debe vivir nunca como texto plano
> en un archivo versionado, en una nota de iCloud, en una captura de pantalla
> ni en el chat con la IA. Tiene que estar **encriptado en reposo** y
> **descifrado solo en el momento en que el proceso lo necesita**.

Este manual explica cómo se gestionan los secretos en **Iztack-Finance**
siguiendo la regla de "defensa en profundidad":

```
┌─────────────────────────────────────────────────────────────────┐
│  CAPA 1  Disco / Repo  →  cifrado (GPG con `pass`)              │
│  CAPA 2  Transporte    →  .env inyectado solo en memoria (ENV)  │
│  CAPA 3  Aplicación    →  AES-256-GCM (`CryptoManager`)         │
│  CAPA 4  UI            →  Setup Wizard NO muestra secretos      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Inventario de secretos

Estos son los valores que NUNCA deben estar en texto plano en el repo:

| Variable                      | Servicio                | Criticidad |
| ----------------------------- | ----------------------- | ---------- |
| `SECRET_KEY`                  | Cifrado llavero interno | 🔴 Alta    |
| `TELEGRAM_BOT_TOKEN`          | Bot de Telegram         | 🔴 Alta    |
| `GEMINI_API_KEY`              | OCR (Gemini Vision)     | 🔴 Alta    |
| `TWILIO_AUTH_TOKEN`           | WhatsApp inbound        | 🔴 Alta    |
| `GOOGLE_CLIENT_SECRET`        | OAuth Google            | 🟠 Media   |
| `GOOGLE_REFRESH_TOKEN`        | Gmail + Drive           | 🔴 Alta    |
| `GMAIL_SENDER_EMAIL_PASSWORD` | App Password Gmail      | 🔴 Alta    |
| Credenciales de portales      | Amazon, Liverpool, IKEA…| 🔴 Alta    |

El archivo `.env.example` **solo tiene placeholders**, nunca valores reales.

---

## 2. La buena práctica recomendada: `pass` (GPG) + dotenv loader

[`pass`](https://www.passwordstore.org/) es el estándar POSIX para guardar
secretos cifrados con GPG en un directorio `.password-store/`. Lo que hace
famoso a `pass` es:

- Cada secreto es un archivo cifrado con tu **llave GPG privada**.
- El repositorio de secretos puede sincronizarse entre máquinas (incluso a
  un repo privado en GitHub) porque todo va cifrado.
- `pass` se integra con Apple Keychain, macOS Keychain y `gpg-agent`.

### 2.1 Instalación (solo una vez por máquina)

```bash
# macOS
brew install gnupg pass

# Linux (Debian/Ubuntu)
sudo apt-get install -y gnupg pass
```

### 2.2 Generar tu llave GPG (si no tienes una)

```bash
gpg --full-generate-key
# Tipo: RSA and RSA, 4096 bits, sin expiración
# Nombre: Abraham Dev
# Email: <el que uses para firmar commits>
# Passphrase: ⚠️ ESTA ES LA LLAVE MAESTRA. Guárdala en Apple Passwords
#             y/o en tu gestor de contraseñas físico.
```

Tu GPG ID será algo como `3F4A9B…ABCD`. Lo usaremos en el siguiente paso.

### 2.3 Inicializar el almacén `pass`

```bash
pass init "3F4A9B…ABCD"   # ← tu GPG ID
```

Esto crea `~/.password-store/` que es un árbol de archivos `.gpg`.

### 2.4 Guardar los secretos (uno por archivo)

```bash
pass insert iztack/telegram_bot_token
pass insert iztack/gemini_api_key
pass insert iztack/twilio_auth_token
pass insert iztack/google_client_secret
pass insert iztack/google_refresh_token
pass insert iztack/secret_key
pass insert iztack/liverpool_password
pass insert iztack/amazon_password
# … y así con cada portal
```

Para ver un secreto en un momento dado:

```bash
pass show iztack/telegram_bot_token        # te lo descifra al vuelo
```

---

## 3. Cómo se cargan al backend (capa 2)

El backend **no lee** el llavero de `pass` directamente. Lo que hace es
un script `scripts/load_secrets.sh` que:

1. Llama a `pass show` para cada secreto.
2. Los exporta como **variables de entorno** en el proceso actual.
3. Arranca `uvicorn` heredando esas variables.

```bash
#!/usr/bin/env bash
# scripts/load_secrets.sh
# Carga todos los secretos desde `pass` y arranca el backend.
# NUNCA loguea ni persiste los valores a disco.

set -euo pipefail

export SECRET_KEY="$(pass show iztack/secret_key)"
export TELEGRAM_BOT_TOKEN="$(pass show iztack/telegram_bot_token)"
export GEMINI_API_KEY="$(pass show iztack/gemini_api_key)"
export TWILIO_AUTH_TOKEN="$(pass show iztack/twilio_auth_token)"
export GOOGLE_CLIENT_SECRET="$(pass show iztack/google_client_secret)"
export GOOGLE_REFRESH_TOKEN="$(pass show iztack/google_refresh_token)"

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Uso:

```bash
chmod +x scripts/load_secrets.sh
./scripts/load_secrets.sh
```

Los valores **solo existen en la RAM del proceso**. Si el proceso muere,
se evaporan. Si haces `ps aux | grep uvicorn` tampoco aparecen como args
de línea de comandos.

---

## 4. Cómo los cifra el backend (capa 3)

El módulo `backend/app/utils/crypto.py` ya implementa `CryptoManager` con
**AES-256-GCM + PBKDF2 (100k iteraciones)**. Es decir:

- El `SECRET_KEY` (cargado desde `pass`) actúa como **llave maestra**.
- Cada secreto de portal (Liverpool, Amazon…) se cifra con
  `CryptoManager.encrypt(plaintext, context="liverpool")` antes de
  guardarse en la tabla `setup_credentials`.
- El `context` (AAD — Additional Authenticated Data) impide que un
  ciphertext de Liverpool se "lea" como si fuera de Amazon.
- En la BD solo se guarda `(ciphertext, nonce, key_id)`. El `key_id` es
  el `salt` en base64.

```python
# backend/app/modules/setup/service.py (extracto)
from app.utils.crypto import CryptoManager

crypto = CryptoManager(master_key=settings.secret_key)
cipher, nonce, key_id = crypto.encrypt(plaintext, context=portal_name)
```

Para descifrar:

```python
plain = crypto.decrypt(cipher, nonce, key_id, context=portal_name)
```

### Rotación de `SECRET_KEY`

Si alguna vez se filtra la maestra:

1. Genera una nueva: `pass generate -n iztack/secret_key 32`.
2. Vuelve a cifrar TODAS las credenciales en BD con la nueva llave.
3. Actualiza `pass insert iztack/secret_key` con la nueva.
4. Reinicia el backend.

`CryptoManager.encrypt` está diseñado para re-cifrar masivamente: solo se
reusa el mismo `plaintext` y `context` y se reescribe la fila.

---

## 5. Lo que el Setup Wizard NUNCA debe hacer (capa 4)

El wizard (`frontend/app/setup/page.tsx` + `backend/app/modules/setup/`)
tiene que respetar estas reglas de UX:

- ✅ **Sí:** pedir el token una sola vez, validar formato, y devolver un
  "✅ Guardado" sin mostrar el valor de vuelta.
- ❌ **No:** loguear el token en la consola del navegador.
- ❌ **No:** meterlo en `localStorage` o `sessionStorage`.
- ❌ **No:** devolverlo al frontend en respuestas de la API.
- ❌ **No:** permitir "ver" un token ya guardado, solo "rotarlo".

El backend devuelve algo como:

```json
{
  "portal": "liverpool",
  "status": "saved",
  "last4": "…f3A2",
  "created_at": "2026-07-06T12:00:00Z"
}
```

Y **nunca** el token completo.

---

## 6. Backups cifrados

`~/.password-store/` se puede sincronizar tal cual a un repo privado de
GitHub. Como todo va cifrado con tu GPG, si el repo se filtra, el atacante
necesita tu llave privada (que está en tu máquina, no en el repo).

```bash
# Subir a un repo privado de backup
cd ~/.password-store
git init && git remote add origin git@github.com:TU_USUARIO/iztack-secrets.git
git add . && git commit -m "secrets snapshot" && git push -u origin master
```

Recomendado: hacer esto **solo cuando se añadan secretos nuevos** y
mantener el repo como **privado e invitable**.

---

## 7. Qué pasa si me roban la laptop

- El disco debería estar cifrado con **FileVault** (macOS) o **LUKS**
  (Linux). Si no lo está, **hazlo hoy**.
- `pass` descifra con la passphrase de GPG, y `gpg-agent` puede tener
  TTL de 0 para que la pida cada vez.
- Si el ladrón no tiene tu passphrase GPG, los secretos son inútiles
  aunque clone el `~/.password-store/`.

---

## 8. Resumen — checklist de "lo que NUNCA debes hacer"

- [ ] ❌ Subir un `.env` con valores reales a GitHub (ni siquiera a un
      repo privado "temporal").
- [ ] ❌ Pegar un token en una nota de Apple Notes / iCloud Drive.
- [ ] ❌ Capturar de pantalla un secreto (queda en Photos y en iCloud).
- [ ] ❌ Mandar el token por WhatsApp, Telegram o email.
- [ ] ❌ Pegar el token en el chat con la IA y dejarlo ahí para que se
      quede en el historial.
- [ ] ❌ Imprimir un token en papel y dejarlo pegado al monitor.
- [ ] ❌ Compartir el `.env` por AirDrop o por USB.

- [ ] ✅ Usar `pass insert` y un GPG de 4096 bits.
- [ ] ✅ Cargar los secretos al proceso con `scripts/load_secrets.sh`.
- [ ] ✅ Dejar que `CryptoManager` los cifre antes de tocar la BD.
- [ ] ✅ Guardar la passphrase de GPG en Apple Passwords / Google
      Password Manager / 1Password / Bitwarden.
- [ ] ✅ Rotar cualquier secreto en cuanto sepas que estuvo expuesto.