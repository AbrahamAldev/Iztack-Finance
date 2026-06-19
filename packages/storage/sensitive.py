"""
SensitiveStorage - Almacenamiento cifrado para datos sensibles.
Cifra cada archivo con AES-256-GCM antes de guardar en disco.
"""
import os
from pathlib import Path
from typing import Optional, List
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class SensitiveStorage:
    """Almacenamiento con cifrado en reposo."""

    BASE_PATH = Path("/data/sensitive")

    def __init__(self, encryption_key: Optional[str] = None):
        self.base_path = self.BASE_PATH
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Usar key separada de la de la app
        key_hex = encryption_key or os.environ.get("SENSITIVE_ENCRYPTION_KEY")
        if not key_hex:
            # Generar key por defecto para desarrollo
            import secrets
            key_hex = secrets.token_hex(32)
            os.environ["SENSITIVE_ENCRYPTION_KEY"] = key_hex
        
        self.key = bytes.fromhex(key_hex)
        self._aesgcm = AESGCM(self.key)

    def put(self, name: str, content: bytes) -> str:
        """Guardar archivo cifrado."""
        nonce = os.urandom(12)
        encrypted = self._aesgcm.encrypt(nonce, content, name.encode())
        
        # Formato: nonce (12 bytes) + encrypted
        filepath = self.base_path / f"{name}.enc"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_bytes(nonce + encrypted)
        
        return str(filepath)

    def get(self, name: str) -> Optional[bytes]:
        """Leer y descifrar archivo."""
        filepath = self.base_path / f"{name}.enc"
        if not filepath.exists():
            return None
        
        data = filepath.read_bytes()
        nonce = data[:12]
        encrypted = data[12:]
        
        return self._aesgcm.decrypt(nonce, encrypted, name.encode())

    def delete(self, name: str) -> bool:
        """Eliminar archivo cifrado."""
        filepath = self.base_path / f"{name}.enc"
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def exists(self, name: str) -> bool:
        """Verificar si archivo cifrado existe."""
        return (self.base_path / f"{name}.enc").exists()

    def list(self) -> List[str]:
        """Listar archivos cifrados (sin extensión .enc)."""
        return [p.stem for p in self.base_path.glob("*.enc")]