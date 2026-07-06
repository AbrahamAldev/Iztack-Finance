#!/usr/bin/env bash
# scripts/load_secrets.sh
# Carga todos los secretos desde `pass` (GPG) y arranca el backend.
# Los valores solo viven en la RAM del proceso: nunca se persisten a disco
# en texto plano.
#
# Prerequisito (una sola vez):
#   brew install gnupg pass
#   gpg --full-generate-key                       # ed25519 + cv25519
#   pass init "<TU_GPG_FINGERPRINT>"
#
#   pass insert -m iztack/telegram/bot_token      # token del bot
#   pass insert -m iztack/crypto/aes_db           # AES-256-GCM 32B hex
#   pass insert -m iztack/crypto/aes_jwt          # AES-256-GCM 32B hex
#   pass insert -m iztack/crypto/aes_drive        # AES-256-GCM 32B hex
#
#   # Opcionales (cuando apliquen)
#   pass insert -m iztack/gemini/api_key
#   pass insert -m iztack/google/client_id
#   pass insert -m iztack/google/client_secret
#   pass insert -m iztack/google/refresh_token
#   pass insert -m iztack/google/drive_folder_id
#   pass insert -m iztack/gmail/sender_email
#   pass insert -m iztack/twilio/account_sid
#   pass insert -m iztack/twilio/auth_token
#   pass insert -m iztack/twilio/whatsapp_number
#   pass insert -m iztack/telegram/chat_id_authorized
#
# Uso:
#   ./scripts/load_secrets.sh                      # arranca uvicorn
#   ./scripts/load_secrets.sh --print-env          # exporta a stdout (eval-able)
#   ./scripts/load_secrets.sh --write-env FILE     # escribe .env cifrado AES-256-GCM
#
# NUNCA loguees los valores. NUNCA redirijas stdout a un archivo en claro.

set -euo pipefail

# --- Helpers ----------------------------------------------------------------

fail_if_missing() {
    if [[ -z "${!1:-}" ]]; then
        echo "❌ No se pudo cargar '$1' desde pass:$2" >&2
        echo "   Ejecuta: pass insert -m $2" >&2
        exit 1
    fi
}

load_secret() {
    local var="$1" path="$2" required="${3:-true}" value
    if ! value="$(pass show "$path" 2>/dev/null)"; then
        if [[ "$required" == "true" ]]; then
            echo "❌ pass show '$path' falló (¿no existe o passphrase GPG incorrecta?)" >&2
            exit 1
        else
            echo "⚠️  $var omitido (pass:$path no existe, no es obligatorio)"
            return 0
        fi
    fi
    export "$var=$value"
    echo "✅ $var cargado desde pass:$path"
}

# --- Carga de secretos ------------------------------------------------------

echo "🔐 Cargando secretos desde pass (GPG)…"

# Críticos (obligatorios)
load_secret TELEGRAM_BOT_TOKEN        iztack/telegram/bot_token
load_secret AES_DB_KEY                iztack/crypto/aes_db
load_secret AES_JWT_KEY               iztack/crypto/aes_jwt
load_secret AES_DRIVE_KEY             iztack/crypto/aes_drive
load_secret SECRET_KEY                iztack/crypto/secret_key false

# Opcionales (se cargan si existen)
load_secret TELEGRAM_CHAT_ID_AUTHORIZED iztack/telegram/chat_id_authorized false
load_secret GEMINI_API_KEY            iztack/gemini/api_key                false
load_secret GOOGLE_CLIENT_ID          iztack/google/client_id              false
load_secret GOOGLE_CLIENT_SECRET      iztack/google/client_secret          false
load_secret GOOGLE_REFRESH_TOKEN      iztack/google/refresh_token          false
load_secret GOOGLE_DRIVE_FOLDER_ID    iztack/google/drive_folder_id        false
load_secret GMAIL_SENDER_EMAIL        iztack/gmail/sender_email            false
load_secret TWILIO_ACCOUNT_SID        iztack/twilio/account_sid            false
load_secret TWILIO_AUTH_TOKEN         iztack/twilio/auth_token             false
load_secret TWILIO_WHATSAPP_NUMBER    iztack/twilio/whatsapp_number        false

# --- Variables no sensibles (las puede leer de .env) ------------------------

if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
    echo "✅ Variables no sensibles cargadas desde .env"
fi

# --- Modos de salida --------------------------------------------------------

ACTION="${1:-run}"

case "$ACTION" in
    --print-env)
        # Exporta las variables para que las capture el shell padre con `eval`
        # shellcheck disable=SC2154
        for v in TELEGRAM_BOT_TOKEN AES_DB_KEY AES_JWT_KEY AES_DRIVE_KEY \
                 SECRET_KEY TELEGRAM_CHAT_ID_AUTHORIZED GEMINI_API_KEY \
                 GOOGLE_CLIENT_ID GOOGLE_CLIENT_SECRET GOOGLE_REFRESH_TOKEN \
                 GOOGLE_DRIVE_FOLDER_ID GMAIL_SENDER_EMAIL \
                 TWILIO_ACCOUNT_SID TWILIO_AUTH_TOKEN TWILIO_WHATSAPP_NUMBER; do
            if [[ -n "${!v:-}" ]]; then
                printf 'export %s=%q\n' "$v" "${!v}"
            fi
        done
        ;;
    --write-env)
        target="${2:?Falta el archivo destino}"
        tmp="$(mktemp)"
        trap 'shred -u "$tmp" 2>/dev/null || rm -f "$tmp"' EXIT
        {
            echo "# Generado por scripts/load_secrets.sh --write-env"
            echo "# Cifrado con AES-256-GCM usando AES_DB_KEY"
            echo "# Para descifrar: openssl enc -d -aes-256-gcm -in FILE -pass pass:\$AES_DB_KEY"
            echo "# $(date -u +%Y-%m-%dT%H:%M:%SZ)"
            echo
            for v in TELEGRAM_BOT_TOKEN AES_DB_KEY AES_JWT_KEY AES_DRIVE_KEY \
                     SECRET_KEY TELEGRAM_CHAT_ID_AUTHORIZED GEMINI_API_KEY \
                     GOOGLE_CLIENT_ID GOOGLE_CLIENT_SECRET GOOGLE_REFRESH_TOKEN \
                     GOOGLE_DRIVE_FOLDER_ID GMAIL_SENDER_EMAIL \
                     TWILIO_ACCOUNT_SID TWILIO_AUTH_TOKEN TWILIO_WHATSAPP_NUMBER; do
                if [[ -n "${!v:-}" ]]; then
                    printf '%s=%q\n' "$v" "${!v}"
                fi
            done
        } > "$tmp"
        openssl enc -aes-256-gcm -salt -pbkdf2 -iter 200000 \
            -in "$tmp" \
            -out "$target" \
            -pass "pass:${AES_DB_KEY}"
        shred -u "$tmp" 2>/dev/null || rm -f "$tmp"
        trap - EXIT
        echo "✅ .env cifrado escrito en $target (AES-256-GCM, PBKDF2 200k iter)"
        ;;
    run|"" )
        HOST="${HOST:-0.0.0.0}"
        PORT="${PORT:-8000}"
        WORKERS="${WORKERS:-1}"

        echo "🚀 Arrancando uvicorn en ${HOST}:${PORT} (workers=${WORKERS})…"

        exec uvicorn app.main:app \
            --host "${HOST}" \
            --port "${PORT}" \
            --workers "${WORKERS}"
        ;;
    *)
        echo "Uso: $0 [--print-env | --write-env FILE | run]" >&2
        exit 64
        ;;
esac