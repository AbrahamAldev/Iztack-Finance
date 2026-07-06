#!/usr/bin/env bash
# scripts/load_secrets.sh
# Carga todos los secretos desde `pass` (GPG) y arranca el backend.
# Los valores solo viven en la RAM del proceso: nunca se persisten a disco.
#
# Prerequisito:
#   brew install gnupg pass
#   gpg --full-generate-key
#   pass init "<TU_GPG_ID>"
#   pass insert iztack/secret_key
#   pass insert iztack/telegram_bot_token
#   pass insert iztack/gemini_api_key
#   pass insert iztack/twilio_auth_token
#   pass insert iztack/google_client_secret
#   pass insert iztack/google_refresh_token
#   pass insert iztack/google_client_id
#   pass insert iztack/google_drive_folder_id
#   pass insert iztack/gmail_sender_email
#
# Uso:
#   chmod +x scripts/load_secrets.sh
#   ./scripts/load_secrets.sh
#
# En docker-compose se usa docker secrets o se monta /run/secrets/*.
# NUNCA loguees los valores. NUNCA redirijas a un archivo.

set -euo pipefail

# --- Helpers ----------------------------------------------------------------

# fail_if_missing <var> <pass-path>
fail_if_missing() {
    if [[ -z "${!1:-}" ]]; then
        echo "❌ No se pudo cargar '$1' desde pass:$2" >&2
        echo "   Ejecuta: pass insert $2" >&2
        exit 1
    fi
}

# load_secret <env-var> <pass-path>
load_secret() {
    local value
    if ! value="$(pass show "$2" 2>/dev/null)"; then
        echo "❌ pass show '$2' falló (¿no existe o passphrase GPG incorrecta?)" >&2
        exit 1
    fi
    export "$1=$value"
    # No imprimir el valor. Solo confirmar.
    echo "✅ $1 cargado desde pass:$2"
}

# --- Carga de secretos ------------------------------------------------------

echo "🔐 Cargando secretos desde pass (GPG)…"

load_secret SECRET_KEY                iztack/secret_key
load_secret TELEGRAM_BOT_TOKEN        iztack/telegram_bot_token
load_secret TELEGRAM_CHAT_ID_AUTHORIZED iztack/telegram_chat_id_authorized
load_secret GEMINI_API_KEY            iztack/gemini_api_key
load_secret TWILIO_ACCOUNT_SID        iztack/twilio_account_sid
load_secret TWILIO_AUTH_TOKEN         iztack/twilio_auth_token
load_secret TWILIO_WHATSAPP_NUMBER    iztack/twilio_whatsapp_number
load_secret GOOGLE_CLIENT_ID          iztack/google_client_id
load_secret GOOGLE_CLIENT_SECRET      iztack/google_client_secret
load_secret GOOGLE_REFRESH_TOKEN      iztack/google_refresh_token
load_secret GOOGLE_DRIVE_FOLDER_ID    iztack/google_drive_folder_id
load_secret GMAIL_SENDER_EMAIL        iztack/gmail_sender_email

# --- Variables no sensibles (las puede leer de .env) ------------------------

if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
    echo "✅ Variables no sensibles cargadas desde .env"
fi

# --- Arranque ---------------------------------------------------------------

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-1}"

echo "🚀 Arrancando uvicorn en ${HOST}:${PORT} (workers=${WORKERS})…"

exec uvicorn app.main:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --workers "${WORKERS}"