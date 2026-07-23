"""
Multi-Agent API routes — prototype endpoints for the agent system.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import OrchestratorAgent
from app.database.connection import get_db
from app.database.models import User
from app.modules.auth.deps import get_current_user
from app.modules.tickets.tracer import trace_step

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["Agents"])


@router.post("/chat")
async def agent_chat(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Chat endpoint powered by the multi-agent orchestrator.
    Routes fiscal/financial questions to specialist agents.
    """
    message = data.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Mensaje requerido")

    orchestrator = OrchestratorAgent()
    result = await orchestrator.process_chat_message(
        message=message,
        user_id=current_user.id,
        db_session=db,
    )

    trace_step(
        user_id=current_user.id,
        step="agent_chat",
        status="ok" if result.success else "error",
        details={"intent": result.output.get("intent") if result.success else None, "error": result.error},
    )

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error or "Error del agente")

    response_text = ""
    intent = result.output.get("intent", "general")

    if intent in ("fiscal", "financial"):
        specialist = result.output.get("specialist_response", {})
        response_text = specialist.get("response", "No obtuve respuesta del especialista")
        sources = specialist.get("sources", [])
    else:
        response_text = result.output.get("response", "No obtuve respuesta")
        sources = []

    return {
        "success": True,
        "intent": intent,
        "response": response_text,
        "sources": sources,
    }


@router.post("/process-ticket")
async def agent_process_ticket(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Prototype endpoint to process a base64 ticket image through the agent pipeline.
    """
    import base64

    image_b64 = data.get("image_base64", "")
    if not image_b64:
        raise HTTPException(status_code=400, detail="image_base64 requerido")

    try:
        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]
        image_bytes = base64.b64decode(image_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="image_base64 inválido")

    orchestrator = OrchestratorAgent()
    result = await orchestrator.process_ticket_image(
        image_bytes=image_bytes,
        user_id=current_user.id,
    )

    trace_step(
        user_id=current_user.id,
        step="agent_ticket",
        status="ok" if result.success else "error",
        details={"error": result.error},
    )

    if not result.success:
        return {
            "success": False,
            "error": result.error,
            "user_message": result.user_message,
        }

    return {
        "success": True,
        "ocr": result.output.get("ocr"),
        "validation": result.output.get("validation"),
        "billing": result.output.get("billing"),
    }
