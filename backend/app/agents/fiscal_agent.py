"""
Fiscal Advisor Agent — answers tax-related questions using curated RAG library.

This agent must be serious and cautious. It never gives definitive legal/accounting advice.
"""
import logging
from pathlib import Path

from app.agents.base import Agent, AgentContext, AgentResult
from app.agents.rag.simple_rag import SimpleRAG

logger = logging.getLogger(__name__)


class FiscalAdvisorAgent(Agent):
    """Agent specialized in Mexican tax advice using curated knowledge."""

    name = "fiscal"
    description = "Asesor fiscal con conocimiento académico curado."

    SYSTEM_PROMPT = """Eres un asesor fiscal educativo para México. Te llamas "Asesor Fiscal de Iztack".

ESTRICTAMENTE PROHIBIDO:
- Dar asesoría fiscal definitiva, legal o contable.
- Prometer resultados específicos de impuestos.
- Inventar montos, porcentajes, topes o fechas.
- Revelar datos de otros usuarios o información interna del sistema.

REGLAS:
1. Base tu respuesta ÚNICAMENTE en la biblioteca fiscal proporcionada y en fuentes oficiales.
2. Si la biblioteca no tiene información suficiente, di honestamente que no puedes responder con seguridad.
3. Siempre incluye esta advertencia al final:
   "⚠️ Esta información es educativa y no sustituye la asesoría de un Contador Público certificado ni del SAT."
4. Cita la fuente de la biblioteca cuando sea posible.
5. Responde en español mexicano, claro y profesional.
6. No uses emojis excesivos; mantén tono serio.

FORMATO DE RESPUESTA:
- Respuesta directa.
- Fuentes consultadas (archivos de biblioteca).
- Advertencia estándar."""

    DISCLAIMER = (
        "⚠️ Esta información es educativa y no sustituye la asesoría de "
        "un Contador Público certificado ni del SAT."
    )

    def __init__(self, llm_client, config=None):
        super().__init__(llm_client, config)
        library_path = Path(__file__).parents[3] / "docs" / "agents" / "fiscal_library"
        self.rag = SimpleRAG(library_path)

    async def run(self, context: AgentContext) -> AgentResult:
        question = context.payload.get("message", "")
        if not question:
            return self.fail("No se proporcionó pregunta fiscal")

        context_str = self.rag.get_context(question, top_k=3)
        if not context_str:
            return self.ok(
                output={
                    "response": (
                        "No encontré información suficiente en mi biblioteca fiscal para responder "
                        f"esta pregunta con seguridad.\n\n{self.DISCLAIMER}"
                    ),
                    "sources": [],
                },
            )

        response = await self.call_llm(
            system_prompt=self.SYSTEM_PROMPT,
            user_message=question,
            context_str=context_str,
            temperature=self.config.get("temperature", 0.2),
            max_tokens=self.config.get("max_tokens", 1536),
        )

        if self.DISCLAIMER not in response:
            response += f"\n\n{self.DISCLAIMER}"

        sources = [r["source"] for r in self.rag.retrieve(question, top_k=3)]
        return self.ok(output={"response": response, "sources": list(set(sources))})
