import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

STORAGE_ROOT = os.getenv("STORAGE_ROOT", "/data/storage")
MAX_USER_STORAGE_BYTES = 1 * 1024 * 1024 * 1024  # 1 GB

logger = logging.getLogger(__name__)


class StorageError(Exception):
    pass


class QuotaExceededError(StorageError):
    pass


class FileNotFoundError_(StorageError):
    pass


class LocalStorageService:

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user_root = Path(STORAGE_ROOT) / user_id
        self.tickets_dir = self.user_root / "tickets"
        self.invoices_dir = self.user_root / "invoices"

    def _ensure_dirs(self):
        self.tickets_dir.mkdir(parents=True, exist_ok=True)
        self.invoices_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Quota
    # ------------------------------------------------------------------

    def get_usage(self) -> dict:
        total = 0
        for f in self.user_root.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
        return {
            "used_bytes": total,
            "max_bytes": MAX_USER_STORAGE_BYTES,
            "used_pct": round((total / MAX_USER_STORAGE_BYTES) * 100, 1),
            "free_bytes": MAX_USER_STORAGE_BYTES - total,
        }

    def _check_quota(self, additional: int):
        usage = self.get_usage()
        if usage["used_bytes"] + additional > usage["max_bytes"]:
            raise QuotaExceededError(
                f"Almacenamiento lleno ({usage['used_pct']}%). "
                f"Libera espacio o contacta a soporte."
            )

    def _count_size(self, path: Path) -> int:
        total = 0
        if path.is_file():
            return path.stat().st_size
        for f in path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
        return total

    # ------------------------------------------------------------------
    # Tickets
    # ------------------------------------------------------------------

    def save_ticket_image(self, ticket_id: str, original: bytes, processed: Optional[bytes] = None) -> dict:
        self._ensure_dirs()
        size = len(original) + (len(processed) if processed else 0)
        self._check_quota(size)

        ticket_dir = self.tickets_dir / ticket_id
        ticket_dir.mkdir(parents=True, exist_ok=True)

        orig_path = ticket_dir / "original.jpg"
        orig_path.write_bytes(original)

        proc_path = None
        if processed:
            proc_path = ticket_dir / "processed.jpg"
            proc_path.write_bytes(processed)

        return {
            "original": str(orig_path),
            "processed": str(proc_path) if proc_path else None,
        }

    def get_ticket_image(self, ticket_id: str, variant: str = "original") -> Optional[bytes]:
        path = self.tickets_dir / ticket_id / f"{variant}.jpg"
        if not path.exists():
            return None
        return path.read_bytes()

    def delete_ticket(self, ticket_id: str) -> bool:
        ticket_dir = self.tickets_dir / ticket_id
        if not ticket_dir.exists():
            return False
        shutil.rmtree(ticket_dir)
        return True

    def list_tickets(self) -> list:
        self._ensure_dirs()
        results = []
        for tdir in sorted(self.tickets_dir.iterdir()):
            if not tdir.is_dir():
                continue
            orig = tdir / "original.jpg"
            proc = tdir / "processed.jpg"
            entry = {
                "id": tdir.name,
                "type": "ticket",
                "original_size": orig.stat().st_size if orig.exists() else 0,
                "processed_size": proc.stat().st_size if proc.exists() else 0,
                "has_processed": proc.exists(),
                "created_at": datetime.fromtimestamp(orig.stat().st_mtime).isoformat() if orig.exists() else "",
            }
            results.append(entry)
        return results

    # ------------------------------------------------------------------
    # Invoices
    # ------------------------------------------------------------------

    def save_invoice_file(self, invoice_id: str, pdf_bytes: Optional[bytes], xml_bytes: Optional[bytes]) -> dict:
        self._ensure_dirs()
        size = (len(pdf_bytes) if pdf_bytes else 0) + (len(xml_bytes) if xml_bytes else 0)
        self._check_quota(size)

        inv_dir = self.invoices_dir / invoice_id
        inv_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = None
        if pdf_bytes:
            pdf_path = inv_dir / "factura.pdf"
            pdf_path.write_bytes(pdf_bytes)

        xml_path = None
        if xml_bytes:
            xml_path = inv_dir / "factura.xml"
            xml_path.write_bytes(xml_bytes)

        return {
            "pdf": str(pdf_path) if pdf_path else None,
            "xml": str(xml_path) if xml_path else None,
        }

    def get_invoice_file(self, invoice_id: str, ext: str = "pdf") -> Optional[bytes]:
        path = self.invoices_dir / invoice_id / f"factura.{ext}"
        if not path.exists():
            return None
        return path.read_bytes()

    def delete_invoice(self, invoice_id: str) -> bool:
        inv_dir = self.invoices_dir / invoice_id
        if not inv_dir.exists():
            return False
        shutil.rmtree(inv_dir)
        return True

    def list_invoices(self) -> list:
        self._ensure_dirs()
        results = []
        for idir in sorted(self.invoices_dir.iterdir()):
            if not idir.is_dir():
                continue
            pdf = idir / "factura.pdf"
            xml = idir / "factura.xml"
            entry = {
                "id": idir.name,
                "type": "invoice",
                "has_pdf": pdf.exists(),
                "has_xml": xml.exists(),
                "pdf_size": pdf.stat().st_size if pdf.exists() else 0,
                "xml_size": xml.stat().st_size if xml.exists() else 0,
                "created_at": datetime.fromtimestamp(pdf.stat().st_mtime).isoformat() if pdf.exists() else "",
            }
            results.append(entry)
        return results

    # ------------------------------------------------------------------
    # Generic
    # ------------------------------------------------------------------

    def list_all(self) -> list:
        return self.list_tickets() + self.list_invoices()

    def delete_by_id(self, file_id: str) -> bool:
        ticket_dir = self.tickets_dir / file_id
        if ticket_dir.exists():
            shutil.rmtree(ticket_dir)
            return True
        inv_dir = self.invoices_dir / file_id
        if inv_dir.exists():
            shutil.rmtree(inv_dir)
            return True
        return False
