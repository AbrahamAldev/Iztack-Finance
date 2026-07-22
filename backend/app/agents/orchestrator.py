"""
Orchestrator Agent — coordinates all other agents.

Receives events, decides which agents to run, and handles errors gracefully.
"""
import logging
from typing import Dict, Type

from app.utils.llm import LLMClient
from app.agents.base import Agent, AgentContext, AgentResult
from app.agents.config import AgentConfig
from app.agents.ocr_agent import OCRAgent
from app.agents.chat_agent import ChatAgent
from app.agents.validator_agent import ValidatorAgent
from app.agents.billing_agent import BillingAgent
from app.agents.librarian_agent import LibrarianAgent
from app.agents.fiscal_agent import FiscalAdvisorAgent
from app.agents.financial_agent import FinancialAdvisorAgent
from app.modules.tickets.tracer import trace_step

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Central orchestrator for the multi-agent system."""

    name = "orchestrator"
    description = "Coordina agentes especializados y maneja el flujo de trabajo."

    AGENT_REGISTRY: Dict[str, Type[Agent]] = {
        "ocr": OCRAgent,
        "chat": ChatAgent,
        "validator": ValidatorAgent,
        "billing": BillingAgent,
        "librarian": LibrarianAgent,
        "fiscal": FiscalAdvisorAgent,
        "financial": FinancialAdvisorAgent,
    }

    def __init__(self):
        self._llm = None

    def _get_llm(self) -> LLMClient:
        if self._llm is None:
            import os
            api_key = os.environ.get("OPENROUTER_API_KEY", "")
            self._llm = LLMClient(api_key) if api_key else None
        return self._llm

    def _get_agent(self, agent_name: str) -> Agent:
        agent_class = self.AGENT_REGISTRY.get(agent_name)
        if not agent_class:
            raise ValueError(f"Agente desconocido: {agent_name}")
        config = AgentConfig.get(agent_name)
        return agent_class(self._get_llm(), config)

    async def process_ticket_image(self, image_bytes: bytes, user_id: str) -> AgentResult:
        """Main workflow for processing a ticket image."""
        trace_step(user_id, "orchestrator_ticket_start", status="ok")

        # 1. OCR
        ctx = AgentContext(user_id=user_id, payload={"image_bytes": image_bytes})
        ocr_result = await self._get_agent("ocr").run(ctx)
        if not ocr_result.success:
            trace_step(user_id, "orchestrator_ticket_end", status="error", details={"step": "ocr"})
            return ocr_result

        # 2. Validation
        ctx.payload = {"ocr_data": ocr_result.output.model_dump() if hasattr(ocr_result.output, "model_dump") else ocr_result.output}
        validation_result = await self._get_agent("validator").run(ctx)

        if not validation_result.output.get("valid"):
            return AgentResult(
                success=False,
                agent_name=self.name,
                output={"ocr": ocr_result.output, "validation": validation_result.output},
                error="Datos OCR no validados",
                user_message=(
                    "⚠️ La foto se procesó pero detecté posibles inconsistencias. "
                    "Por favor revisa los datos antes de continuar."
                ),
            )

        # 3. Billing decision (best effort)
        ctx.payload = {
            "ocr_data": ocr_result.output.model_dump() if hasattr(ocr_result.output, "model_dump") else ocr_result.output,
            "db_session": None,  # To be injected by caller
        }
        billing_result = await self._get_agent("billing").run(ctx)

        trace_step(user_id, "orchestrator_ticket_end", status="ok", details={"billing": billing_result.success})

        return AgentResult(
            success=True,
            agent_name=self.name,
            output={
                "ocr": ocr_result.output,
                "validation": validation_result.output,
                "billing": billing_result.output,
            },
        )

    async def process_chat_message(self, message: str, user_id: str, user_context: str = None) -> AgentResult:
        """Main workflow for handling a user chat message."""
        ctx = AgentContext(user_id=user_id, payload={"message": message, "user_context": user_context})
        chat_result = await self._get_agent("chat").run(ctx)

        if chat_result.output.get("intent") == "fiscal":
            fiscal_result = await self._get_agent("fiscal").run(ctx)
            return AgentResult(
                success=fiscal_result.success,
                agent_name=self.name,
                output={
                    "intent": "fiscal",
                    "specialist_response": fiscal_result.output,
                },
            )

        if chat_result.output.get("intent") == "financial":
            financial_result = await self._get_agent("financial").run(ctx)
            return AgentResult(
                success=financial_result.success,
                agent_name=self.name,
                output={
                    "intent": "financial",
                    "specialist_response": financial_result.output,
                },
            )

        return chat_result
