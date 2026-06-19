"""
LocalStorage - Wrapper sobre sistema de archivos local.
Almacena archivos en /data/storage/ con estructura organizada.
"""
import os
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timezone


class LocalStorage:
    """Operaciones de archivos locales."""

    BASE_PATH = Path("/data/storage")

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or self.BASE_PATH
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Crear estructura de directorios si no existe."""
        dirs = [
            "tickets/raw",
            "tickets/cfdi",
            "reports",
            "printer-temp",
        ]
        for d in dirs:
            (self.base_path / d).mkdir(parents=True, exist_ok=True)

    def put(self, path: str, content: bytes) -> str:
        """Guardar archivo en la ruta especificada."""
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)
        return str(full_path)

    def get(self, path: str) -> Optional[bytes]:
        """Leer archivo."""
        full_path = self.base_path / path
        if not full_path.exists():
            return None
        return full_path.read_bytes()

    def delete(self, path: str) -> bool:
        """Eliminar archivo."""
        full_path = self.base_path / path
        if full_path.exists():
            full_path.unlink()
            return True
        return False

    def exists(self, path: str) -> bool:
        """Verificar si archivo existe."""
        return (self.base_path / path).exists()

    def list(self, prefix: str = "") -> List[str]:
        """Listar archivos bajo un prefijo."""
        base = self.base_path / prefix
        if not base.exists():
            return []
        return [str(p.relative_to(self.base_path)) for p in base.rglob("*") if p.is_file()]

    def size(self, path: str) -> int:
        """Obtener tamaño del archivo en bytes."""
        full_path = self.base_path / path
        return full_path.stat().st_size if full_path.exists() else 0

    def age_days(self, path: str) -> int:
        """Obtener edad del archivo en días."""
        full_path = self.base_path / path
        if not full_path.exists():
            return 0
        mtime = datetime.fromtimestamp(full_path.stat().st_mtime, tz=timezone.utc)
        delta = datetime.now(timezone.utc) - mtime
        return delta.days

    def copy_to(self, src_path: str, dst_path: str) -> bool:
        """Copiar archivo dentro del storage."""
        src = self.base_path / src_path
        dst = self.base_path / dst_path
        if not src.exists():
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True

    def move_to(self, src_path: str, dst_path: str) -> bool:
        """Mover archivo dentro del storage."""
        src = self.base_path / src_path
        dst = self.base_path / dst_path
        if not src.exists():
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return True

    @staticmethod
    def ticket_raw_path(household_id: str, year: int, month: int, sha256: str) -> str:
        """Ruta para fotos de tickets."""
        return f"tickets/raw/{year}/{month:02d}/{sha256}.jpg"

    @staticmethod
    def ticket_cfdi_path(ticket_uuid: str, filename: str) -> str:
        """Ruta para PDFs/XMLs de facturas."""
        return f"tickets/cfdi/{ticket_uuid}/{filename}"

    def get_free_space(self) -> int:
        """Obtener espacio libre en bytes."""
        stat = shutil.disk_usage(self.base_path)
        return stat.free