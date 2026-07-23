"""
Librarian Agent — organizes and stores documents (PDF/XML tickets, invoices).

This agent wraps local filesystem storage and has no LLM by default.
"""
import base64
import logging
import os
from pathlib import Path
from typing import List

from app.agents.base import Agent, AgentContext, AgentResult

logger = logging.getLogger(__name__)

# Base directory for agent-managed documents.
STORAGE_BASE = Path(os.getenv("AGENT_STORAGE_PATH", "/tmp/iztack-agents"))


class LibrarianAgent(Agent):
    """Agent specialized in storing and organizing files locally."""

    name = "librarian"
    description = "Guarda y organiza documentos PDF/XML de tickets y facturas."

    def __init__(self, llm_client=None, config=None):
        # Librarian does not require an LLM
        super().__init__(llm_client or object(), config)
        self.base_path = STORAGE_BASE
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, relative_path: str) -> Path:
        """Resolve a relative path under the base directory, preventing traversal."""
        target = (self.base_path / relative_path).resolve()
        # Ensure the resolved path is still inside base_path
        if not str(target).startswith(str(self.base_path.resolve())):
            raise ValueError("Invalid path: directory traversal detected")
        return target

    async def run(self, context: AgentContext) -> AgentResult:
        operation = context.payload.get("operation")

        if operation == "store_ticket_image":
            return await self._store_ticket_image(context)
        if operation == "store_invoice":
            return await self._store_invoice(context)
        if operation == "list_files":
            return await self._list_files(context)

        return self.fail(f"Operación desconocida: {operation}")

    async def _store_ticket_image(self, context: AgentContext) -> AgentResult:
        household_id = context.payload.get("household_id", "default")
        year = context.payload.get("year")
        month = context.payload.get("month")
        sha256 = context.payload.get("sha256")
        content_b64 = context.payload.get("content")

        if not all([year, month, sha256, content_b64]):
            return self.fail("Faltan parámetros para guardar imagen de ticket")

        try:
            content = base64.b64decode(content_b64)
        except Exception as exc:
            return self.fail(f"Contenido base64 inválido: {exc}")

        relative_path = f"tickets/{household_id}/{year}/{month}/{sha256}.jpg"
        full_path = self._safe_path(relative_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)

        return self.ok(output={"stored_path": str(full_path), "path": relative_path})

    async def _store_invoice(self, context: AgentContext) -> AgentResult:
        ticket_uuid = context.payload.get("ticket_uuid")
        filename = context.payload.get("filename")
        content_b64 = context.payload.get("content")

        if not all([ticket_uuid, filename, content_b64]):
            return self.fail("Faltan parámetros para guardar factura")

        try:
            content = base64.b64decode(content_b64)
        except Exception as exc:
            return self.fail(f"Contenido base64 inválido: {exc}")

        # Local fallback
        relative_path = f"invoices/{ticket_uuid}/{filename}"
        full_path = self._safe_path(relative_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)

        # Try Google Drive if configured
        drive_urls = {}
        try:
            from datetime import date

            from app.modules.almacenamiento.drive_service import DriveStorageService

            store_name = context.payload.get("store_name", "Desconocido")
            purchase_date_str = context.payload.get("purchase_date")
            purchase_date = (
                date.fromisoformat(purchase_date_str)
                if purchase_date_str else date.today()
            )
            has_warranty = context.payload.get("has_warranty", False)
            expense_type = context.payload.get("expense_type", "")

            drive = DriveStorageService()
            file_bytes = content if filename.endswith(".pdf") else None
            xml_bytes = content if filename.endswith(".xml") else None
            drive_urls = await drive.save_invoice(
                store_name=store_name,
                purchase_date=purchase_date,
                pdf_bytes=file_bytes,
                xml_bytes=xml_bytes,
                ticket_id=ticket_uuid,
                has_warranty=has_warranty,
                expense_type=expense_type,
            )
        except Exception as exc:
            logger.warning(f"No se pudo guardar factura en Drive: {exc}")

        return self.ok(
            output={
                "stored_path": str(full_path),
                "path": relative_path,
                "drive_urls": drive_urls,
            }
        )

    async def _list_files(self, context: AgentContext) -> AgentResult:
        prefix = context.payload.get("prefix", "")
        search_path = self._safe_path(prefix) if prefix else self.base_path

        files: List[str] = []
        if search_path.is_dir():
            for item in search_path.rglob("*"):
                if item.is_file():
                    files.append(str(item.relative_to(self.base_path)))

        return self.ok(output={"files": files, "count": len(files)})
