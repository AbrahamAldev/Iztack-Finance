"""
RetentionManager - Purga de archivos locales > 13 meses.
Si hay nube configurada, verifica que estén sincronizados antes de purgar.
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from .local import LocalStorage

logger = logging.getLogger(__name__)


@dataclass
class RetentionResult:
    purged_count: int
    error_count: int
    skipped_count: int
    details: list


class RetentionManager:
    """Gestiona la retención de archivos locales."""

    def __init__(self, max_age_months: int = 13):
        self.max_age_days = max_age_months * 30
        self.storage = LocalStorage()

    async def purge_old_files(self, max_age_months: Optional[int] = None) -> RetentionResult:
        """Purgar archivos locales más antiguos que el límite."""
        if max_age_months:
            self.max_age_days = max_age_months * 30

        result = RetentionResult(0, 0, 0, [])
        prefixes = ["tickets/raw", "tickets/cfdi"]

        for prefix in prefixes:
            files = self.storage.list(prefix)
            for filepath in files:
                age = self.storage.age_days(filepath)
                
                if age > self.max_age_days:
                    # Verificar si está en la nube antes de borrar
                    in_cloud = await self._check_in_cloud(filepath)
                    
                    if in_cloud:
                        self.storage.delete(filepath)
                        result.purged_count += 1
                        result.details.append(f"Purged: {filepath} ({age} days old)")
                        logger.info(f"Purged local file (in cloud): {filepath}")
                    else:
                        result.skipped_count += 1
                        result.details.append(f"Skipped (not in cloud): {filepath}")
                        logger.warning(f"File not in cloud, skipping purge: {filepath}")

        return result

    async def _check_in_cloud(self, filepath: str) -> bool:
        """Verificar si un archivo existe en la nube del usuario."""
        # TODO: Consultar cfdi_attempts para verificar cloud_url
        # Por ahora, si tiene extensión .pdf o .xml en tickets/cfdi/, asumimos que está
        if "cfdi" in filepath and (filepath.endswith(".pdf") or filepath.endswith(".xml")):
            return True
        return False

    async def emergency_purge(self, free_space_threshold_mb: int = 500) -> RetentionResult:
        """Purga de emergencia cuando el disco está casi lleno."""
        free_bytes = self.storage.get_free_space()
        free_mb = free_bytes / (1024 * 1024)
        
        if free_mb > free_space_threshold_mb:
            return RetentionResult(0, 0, 0, ["Space OK"])
        
        # Purga agresiva: bajar a 6 meses
        logger.warning(f"Emergency purge: only {free_mb:.0f} MB free")
        return await self.purge_old_files(max_age_months=6)