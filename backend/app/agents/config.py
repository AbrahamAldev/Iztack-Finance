"""
Configuration for the multi-agent system.

Models are selected from OpenRouter. DeepSeek is preferred for cost efficiency.
"""
import os
from typing import Dict, Any


class AgentModels:
    """Default model selections per agent role."""

    # Fast, cheap models for "worker" agents
    WORKER = os.getenv("AGENT_WORKER_MODEL", "deepseek/deepseek-chat")

    # More capable models for specialist agents
    SPECIALIST = os.getenv("AGENT_SPECIALIST_MODEL", "deepseek/deepseek-chat")

    # Default fallback
    DEFAULT = os.getenv("AGENT_DEFAULT_MODEL", "deepseek/deepseek-chat")


class AgentConfig:
    """Per-agent configuration (model, temperature, max_tokens)."""

    DEFAULTS: Dict[str, Dict[str, Any]] = {
        "orchestrator": {
            "model": AgentModels.WORKER,
            "temperature": 0.2,
            "max_tokens": 1024,
            "description": "Coordina el flujo de agentes y decide siguiente paso.",
        },
        "ocr": {
            "model": os.getenv("AGENT_OCR_MODEL", "openai/gpt-4o-mini"),
            "temperature": 0.0,
            "max_tokens": 2048,
            "description": "Extrae datos estructurados de tickets.",
        },
        "chat": {
            "model": AgentModels.WORKER,
            "temperature": 0.7,
            "max_tokens": 1024,
            "description": "Atiende conversaciones de usuarios.",
        },
        "validator": {
            "model": AgentModels.WORKER,
            "temperature": 0.1,
            "max_tokens": 1024,
            "description": "Valida coherencia de datos extraídos.",
        },
        "billing": {
            "model": AgentModels.WORKER,
            "temperature": 0.2,
            "max_tokens": 1024,
            "description": "Decide y ejecuta facturación CFDI.",
        },
        "librarian": {
            "model": None,  # No LLM by default
            "temperature": 0.0,
            "max_tokens": 256,
            "description": "Organiza y guarda documentos.",
        },
        "fiscal": {
            "model": AgentModels.SPECIALIST,
            "temperature": 0.2,
            "max_tokens": 1536,
            "description": "Asesoría fiscal con RAG sobre biblioteca fiscal.",
        },
        "financial": {
            "model": AgentModels.SPECIALIST,
            "temperature": 0.3,
            "max_tokens": 1536,
            "description": "Análisis financiero con RAG sobre biblioteca financiera.",
        },
    }

    @classmethod
    def get(cls, agent_name: str) -> Dict[str, Any]:
        return cls.DEFAULTS.get(agent_name, cls.DEFAULTS["orchestrator"]).copy()
