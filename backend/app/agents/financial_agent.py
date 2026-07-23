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

        db_session = context.payload.get("db_session")
        financial_summary = ""
        if db_session and self._is_spending_question(question):
            try:
                from datetime import date

                from app.modules.finanzas.service import FinancialAnalysisService

                service = FinancialAnalysisService(db_session)
                today = date.today()
                report = await service.generate_monthly_report(
                    user_id=context.user_id,
                    year=today.year,
                    month=today.month,
                )
                financial_summary = (
                    f"RESUMEN FINANCIERO REAL DEL USUARIO (periodo {report.period}):\n"
                    f"- Total gastado: ${report.total_spent:,.2f}\n"
                    f"- Categoría principal: {report.by_category[0].category if report.by_category else 'N/A'} "
                    f"({report.by_category[0].percentage if report.by_category else 0}%)\n"
                    f"- Ahorro potencial mensual: ${sum(leak.monthly_savings for leak in report.leaks):,.2f}\n"
                    f"- {len(report.leaks)} fugas de dinero detectadas\n"
                    f"- Meta de ahorro semanal: ${report.savings_goal.get('weekly_target', 0):,.2f}\n\n"
                )
            except Exception as exc:
                logger.warning(f"No se pudo generar resumen financiero: {exc}")

        context_str = self.rag.get_context(question, top_k=3)
        if not context_str and not financial_summary:
            return self.ok(
                output={
                    "response": (
                        "No encontré información suficiente en mi biblioteca financiera para responder "
                        f"esta pregunta con seguridad.\n\n{self.PRO_ADVISOR_NOTICE}"
                    ),
                    "sources": [],
                },
            )

        full_context = f"{financial_summary}\n\n{context_str or ''}".strip()

        response = await self.call_llm(
            system_prompt=self.SYSTEM_PROMPT,
            user_message=question,
            context_str=full_context,
            temperature=self.config.get("temperature", 0.3),
            max_tokens=self.config.get("max_tokens", 1536),
        )

        if "asesor financiero" not in response.lower():
            response += f"\n\n{self.PRO_ADVISOR_NOTICE}"

        sources = [r["source"] for r in self.rag.retrieve(question, top_k=3)]
        return self.ok(output={"response": response, "sources": list(set(sources))})

    @staticmethod
    def _is_spending_question(question: str) -> bool:
        """Detect if the user is asking about their own spending/analysis."""
        keywords = [
            "gasto", "gastos", "reporte", "ahorro", "ahorros", "fuga", "fugas",
            "dinero", "finanzas", "presupuesto", "categoría", "categorias",
            "tienda", "mes", "mensual", "análisis", "analisis", "cuánto gasté",
            "cuanto gaste", "dónde gasto", "donde gasto",
        ]
        q = question.lower()
        return any(k in q for k in keywords)
