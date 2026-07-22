"""
Base classes for the multi-agent system.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from app.utils.llm import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Context shared with an agent during execution."""

    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    session_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def add_to_history(self, role: str, content: str, **kwargs):
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs,
        })


@dataclass
class AgentResult:
    """Result returned by an agent."""

    success: bool
    agent_name: str
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    next_agent: Optional[str] = None
    requires_user_input: bool = False
    user_message: Optional[str] = None


class Agent(ABC):
    """Abstract base class for all agents."""

    name: str = "base_agent"
    description: str = "Agente base"

    def __init__(self, llm_client: LLMClient, config: Optional[Dict[str, Any]] = None):
        self.llm = llm_client
        self.config = config or {}

    @abstractmethod
    async def run(self, context: AgentContext) -> AgentResult:
        """Execute the agent's task. Must be implemented by subclasses."""
        raise NotImplementedError

    def build_messages(
        self,
        system_prompt: str,
        user_message: str,
        context_str: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Build a message list for the LLM."""
        messages = [{"role": "system", "content": system_prompt}]
        if context_str:
            messages.append({
                "role": "system",
                "content": f"## CONTEXTO RELEVANTE\n{context_str}",
            })
        messages.append({"role": "user", "content": user_message})
        return messages

    async def call_llm(
        self,
        system_prompt: str,
        user_message: str,
        context_str: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 1024,
    ) -> str:
        """Call the LLM with the agent's configuration."""
        parts = [f"# INSTRUCCIONES DEL SISTEMA\n{system_prompt}"]
        if context_str:
            parts.append(f"# CONTEXTO RELEVANTE\n{context_str}")
        parts.append(f"# ENTRADA DEL USUARIO\n{user_message}")
        full_prompt = "\n\n---\n\n".join(parts)

        response = await self.llm.chat(
            user_message=full_prompt,
            context=None,
            model=self.config.get("model", "openai/gpt-4o-mini"),
            temperature=temperature if temperature is not None else self.config.get("temperature", 0.3),
            max_tokens=max_tokens,
        )
        if not response or "tuve un problema" in response:
            logger.warning(f"[{self.name}] LLM returned empty/error response")
        return response

    def ok(self, output: Any = None, **kwargs) -> AgentResult:
        return AgentResult(success=True, agent_name=self.name, output=output, **kwargs)

    def fail(self, error: str, **kwargs) -> AgentResult:
        logger.error(f"[{self.name}] {error}")
        return AgentResult(success=False, agent_name=self.name, error=error, **kwargs)
