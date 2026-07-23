"""
Sistema Multi-Agente de Iztack-Finance.

Este paquete contiene agentes especializados que orquestan el procesamiento
de tickets, facturación, asesoría fiscal/financiera y atención al usuario.
"""

from .base import Agent, AgentContext, AgentResult
from .billing_agent import BillingAgent
from .chat_agent import ChatAgent
from .config import AgentConfig, AgentModels
from .financial_agent import FinancialAdvisorAgent
from .fiscal_agent import FiscalAdvisorAgent
from .librarian_agent import LibrarianAgent
from .ocr_agent import OCRAgent
from .orchestrator import OrchestratorAgent
from .validator_agent import ValidatorAgent

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
