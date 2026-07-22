"""
Financial Advisor Agent — answers personal finance questions using curated RAG library.

Focuses on household budgeting, savings, expense optimization, and small business finance.
"""
import logging
from pathlib import Path

from app.agents.base import Agent, AgentContext, AgentResult
from app.agents.rag.simple_rag import SimpleRAG

logger = logging.getLogger(__name__)


class FinancialAdvisorAgent(Agent):
    """Agent specialized in personal and small-business finance advice."""

    name = "financial"
    description = "Asesor financiero con conocimiento académico curado."

    SYSTEM_PROMPT = """Eres un asesor financiero educativo. Te llamas "Asesor Financiero de Iztack".

ESTRICTAMENTE PROHIBIDO:
- Recomendar instrumentos de inversión específicos.
- Prometer rendimientos o resultados financieros.
- Dar asesoría financiera personalizada definitiva.
- Revelar datos de otros usuarios o información interna del sistema.

REGLAS:
1. Base tu respuesta en la biblioteca financiera proporcionada.
2. Ofrece principios generales, ejemplos ilustrativos y buenas prácticas.
3. Si la pregunta involucra deudas complejas, inversiones o situaciones legales, recomienda consultar a un asesor financiero certificado.
4. Usa un tono amigable, claro y motivador.
5. Puedes usar emojis con moderación.
6. Responde en español mexicano.

FORMATO DE RESPUESTA:
- Concepto clave.
- Aplicación práctica.
- Ejemplo simple si aplica.
- Advertencia cuando se requiera asesoría profesional."""

    PRO_ADVISOR_NOTICE = (
        "Para decisiones importantes sobre deudas, inversiones o situaciones complejas, "
        "te recomiendo consultar con un asesor financiero certificado."
    )

    def __init__(self, llm_client, config=None):
        super().__init__(llm_client, config)
        library_path = Path(__file__).parents[3] / "docs" / "agents" / "financial_library"
        self.rag = SimpleRAG(library_path)

    async def run(self, context: AgentContext) -> AgentResult:
        question = context.payload.get("message", "")
        if not question:
            return self.fail("No se proporcionó pregunta financiera")

        context_str = self.rag.get_context(question, top_k=3)
        if not context_str:
            return self.ok(
                output={
                    "response": (
                        "No encontré información suficiente en mi biblioteca financiera para responder "
                        f"esta pregunta con seguridad.\n\n{self.PRO_ADVISOR_NOTICE}"
                    ),
                    "sources": [],
                },
            )

        response = await self.call_llm(
            system_prompt=self.SYSTEM_PROMPT,
            user_message=question,
            context_str=context_str,
            temperature=self.config.get("temperature", 0.3),
            max_tokens=self.config.get("max_tokens", 1536),
        )

        if "asesor financiero" not in response.lower():
            response += f"\n\n{self.PRO_ADVISOR_NOTICE}"

        sources = [r["source"] for r in self.rag.retrieve(question, top_k=3)]
        return self.ok(output={"response": response, "sources": list(set(sources))})
