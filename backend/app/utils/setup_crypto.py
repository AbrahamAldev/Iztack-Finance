"""
Iztack-Finance - Setup Crypto Utilities
Shared AES-256-GCM encryption/decryption for tenant secrets stored in the DB.
"""
import logging
import os
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger(__name__)


def get_or_create_master_key() -> bytes:
    """
    Returns a 32-byte master key, persisting a random one to the configured key
    file if needed. In production, set SETUP_MASTER_KEY or mount an existing key.
    """
    env_key = os.getenv("SETUP_MASTER_KEY")
    if env_key:
        import hashlib
        return hashlib.sha256(env_key.encode()).digest()

    key_file = os.getenv("SETUP_MASTER_KEY_FILE", "/opt/iztack-finance/.setup_key")
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read()

    key = secrets.token_bytes(32)
    try:
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, "wb") as f:
            f.write(key)
        os.chmod(key_file, 0o600)
        logger.info("Generated new master key at %s", key_file)
    except Exception as exc:
        logger.warning("Could not persist master key (%s); using in-memory key", exc)
    return key


def encrypt_secret(plaintext: str, key: bytes, key_id: str = "v1") -> tuple[bytes, str]:
    """Encrypt with AES-256-GCM. Returns (ciphertext_blob, key_id)."""
    aes = AESGCM(key)
    nonce = secrets.token_bytes(12)
    ct = aes.encrypt(nonce, plaintext.encode("utf-8"), associated_data=key_id.encode())
    return nonce + ct, key_id


def decrypt_secret(ciphertext: bytes, key: bytes, key_id: str = "v1") -> str:
    """Decrypt an AES-256-GCM blob produced by encrypt_secret."""
    aes = AESGCM(key)
    nonce = ciphertext[:12]
    ct = ciphertext[12:]
    plaintext = aes.decrypt(nonce, ct, associated_data=key_id.encode())
    return plaintext.decode("utf-8")


def decrypt_tenant_secret(encrypted_blob: bytes | None, key_id: str | None) -> str | None:
    """Decrypt a tenant secret using the configured master key."""
    if not encrypted_blob:
        return None
    try:
        key = get_or_create_master_key()
        return decrypt_secret(encrypted_blob, key, key_id or "v1")
    except Exception as exc:
        logger.error("Failed to decrypt tenant secret: %s", exc)
        return None
