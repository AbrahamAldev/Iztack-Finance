"""
Librarian Agent — organizes and stores documents (PDF/XML tickets, invoices).

This agent wraps storage services and has no LLM by default.
"""
import logging
from pathlib import Path
from typing import Optional

from app.agents.base import Agent, AgentContext, AgentResult
from packages.storage.local import LocalStorage

logger = logging.getLogger(__name__)


class LibrarianAgent(Agent):
    """Agent specialized in storing and organizing files."""

    name = "librarian"
    description = "Guarda y organiza documentos PDF/XML de tickets y facturas."

    def __init__(self, llm_client=None, config=None):
        # Librarian does not require an LLM
        super().__init__(llm_client or object(), config)
        self.storage = LocalStorage()

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
        content = context.payload.get("content")

        if not all([year, month, sha256, content]):
            return self.fail("Faltan parámetros para guardar imagen de ticket")

        path = LocalStorage.ticket_raw_path(household_id, year, month, sha256)
        full_path = self.storage.put(path, content)
        return self.ok(output={"stored_path": full_path, "path": path})

    async def _store_invoice(self, context: AgentContext) -> AgentResult:
        ticket_uuid = context.payload.get("ticket_uuid")
        filename = context.payload.get("filename")
        content = context.payload.get("content")

        if not all([ticket_uuid, filename, content]):
            return self.fail("Faltan parámetros para guardar factura")

        path = LocalStorage.ticket_cfdi_path(ticket_uuid, filename)
        full_path = self.storage.put(path, content)
        return self.ok(output={"stored_path": full_path, "path": path})

    async def _list_files(self, context: AgentContext) -> AgentResult:
        prefix = context.payload.get("prefix", "")
        files = self.storage.list(prefix)
        return self.ok(output={"files": files, "count": len(files)})
