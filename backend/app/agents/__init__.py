"""
Sistema Multi-Agente de Iztack-Finance.

Este paquete contiene agentes especializados que orquestan el procesamiento
de tickets, facturación, asesoría fiscal/financiera y atención al usuario.
"""

from .base import Agent, AgentContext, AgentResult
from .config import AgentConfig, AgentModels
from .orchestrator import OrchestratorAgent
from .ocr_agent import OCRAgent
from .chat_agent import ChatAgent
from .validator_agent import ValidatorAgent
from .billing_agent import BillingAgent
from .librarian_agent import LibrarianAgent
from .fiscal_agent import FiscalAdvisorAgent
from .financial_agent import FinancialAdvisorAgent

__all__ = [
    "Agent",
    "AgentContext",
    "AgentResult",
    "AgentConfig",
    "AgentModels",
    "OrchestratorAgent",
    "OCRAgent",
    "ChatAgent",
    "ValidatorAgent",
    "BillingAgent",
    "LibrarianAgent",
    "FiscalAdvisorAgent",
    "FinancialAdvisorAgent",
]
