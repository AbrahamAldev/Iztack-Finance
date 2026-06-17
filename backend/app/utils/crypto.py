"""
Sistema Financiero - Cryptographic Utilities
AES-256-GCM encryption for storing sensitive credentials.
"""
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoManager:
    """Manages AES-256-GCM encryption/decryption of sensitive data."""

    def __init__(self, master_key: str = None):
        """Initialize with a master key (from settings or auto-generated)."""
        self._master_key = master_key or os.environ.get("SECRET_KEY", "default-dev-key-change-in-prod")
        self._derived_key = None
        self._salt = None
        self._key_id = None

    def _derive_key(self, salt: bytes = None) -> tuple[bytes, bytes]:
        """Derive a 256-bit key using PBKDF2."""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        key = kdf.derive(self._master_key.encode())
        return key, salt

    def encrypt(self, plaintext: str, context: str = "") -> tuple[bytes, bytes, str]:
        """
        Encrypt plaintext with AES-256-GCM.
        Returns (ciphertext, nonce, key_id).
        """
        if not plaintext:
            return None, None, None
        
        key, salt = self._derive_key()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), context.encode())
        
        # key_id is base64 of salt for later key derivation
        key_id = base64.b64encode(salt).decode()
        
        return ciphertext, nonce, key_id

    def decrypt(self, ciphertext: bytes, nonce: bytes, key_id: str, context: str = "") -> str:
        """Decrypt ciphertext with AES-256-GCM."""
        if not ciphertext or not nonce or not key_id:
            return None
        
        salt = base64.b64decode(key_id)
        key, _ = self._derive_key(salt)
        aesgcm = AESGCM(key)
        
        plaintext = aesgcm.decrypt(nonce, ciphertext, context.encode())
        return plaintext.decode()

    def generate_password(self, length: int = 16, use_special: bool = True) -> str:
        """Generate a cryptographically secure random password."""
        import secrets
        import string
        
        chars = string.ascii_letters + string.digits
        if use_special:
            chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
        
        # Ensure at least one of each type
        password = [
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.digits),
        ]
        if use_special:
            password.append(secrets.choice("!@#$%^&*()-_=+[]{}|;:,.<>?"))
        
        # Fill the rest
        password.extend(secrets.choice(chars) for _ in range(length - len(password)))
        
        # Shuffle
        secrets.SystemRandom().shuffle(password)
        return "".join(password)

    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key."""
        import secrets
        return secrets.token_hex(32)  # 64-character hex string

    @staticmethod
    def generate_key_id() -> str:
        """Generate a unique key identifier."""
        import uuid
        return str(uuid.uuid4())