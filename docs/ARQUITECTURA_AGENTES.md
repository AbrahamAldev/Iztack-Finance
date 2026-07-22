# 🤖 Arquitectura Multi-Agente — Iztack-Finance

## Visión

Iztack-Finance evoluciona de un backend monolítico con llamadas directas a LLM hacia un **sistema multi-agente orquestado**, donde cada agente especializado tiene responsabilidades claras, prompts específicos y herramientas limitadas. Esto mejora la mantenibilidad, la trazabilidad y la calidad de respuestas en dominios críticos (fiscal y financiero).

## Filosofía de diseño

1. **Un agente, una responsabilidad.** Cada agente hace una sola cosa bien.
2. **Orquestador único.** Solo el `OrchestratorAgent` decide qué agentes ejecutar y en qué orden.
3. **Contexto explícito.** Los agentes se comunican a través de mensajes estructurados, no variables globales.
4. **Modelos según la tarea.**
   - **Obreros:** modelos rápidos y baratos (`deepseek-chat` free tier u OpenRouter free models).
   - **Especialistas:** modelos más potentes para fiscal/financiero (`deepseek-chat` Pro, `claude-3.5-sonnet`, `gpt-4o`).
5. **RAG para especialistas.** Los agentes fiscal y financiero usan bibliotecas curatorias en Markdown como contexto académico.
6. **Trazabilidad total.** Cada decisión de agente se guarda en `PipelineTrace`.

## Mapa de agentes

| Agente | Rol | Modelo recomendado | Prioridad |
|--------|-----|-------------------|-----------|
| `OCRAgent` | Extrae estructura de tickets desde imágenes | `deepseek-chat` / `gpt-4o-mini` | P0 |
| `ChatAgent` | Atiende conversaciones de usuarios (web/Telegram) | `deepseek-chat` | P0 |
| `ValidatorAgent` | Valida coherencia de datos OCR (totales, duplicados, fechas) | `deepseek-chat` / `gpt-4o-mini` | P1 |
| `BillingAgent` | Ejecuta facturación CFDI vía Playwright + decisión LLM | `deepseek-chat` | P1 |
| `LibrarianAgent` | Guarda y organiza PDF/XML en Drive/local | No LLM (lógica Python) | P1 |
| `FiscalAdvisorAgent` | Asesoría fiscal con RAG sobre biblioteca fiscal | `deepseek-chat` Pro / `claude-3.5-sonnet` | P2 |
| `FinancialAdvisorAgent` | Análisis financiero con RAG sobre biblioteca financiera | `deepseek-chat` Pro / `claude-3.5-sonnet` | P2 |
| `OrchestratorAgent` | Recibe eventos, decide flujo, maneja errores | `deepseek-chat` / `gpt-4o-mini` | P0 |

## Flujo típico: usuario sube un ticket

```
Usuario sube foto
        │
        ▼
┌─────────────────┐
│ Orchestrator    │──► "Nuevo ticket recibido"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OCRAgent        │──► Extrae tienda, fecha, productos, total
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ValidatorAgent  │──► Valida totales, duplicados, fechas
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌─────────┐
│Billing │ │Librarian│
│Agent   │ │Agent    │
└────────┘ └─────────┘
    │         │
    ▼         ▼
┌─────────────────┐
│ Orchestrator    │──► Responde al usuario con resumen
└─────────────────┘
```

## Flujo típico: usuario pregunta algo fiscal

```
Usuario: "¿puedo deducir mi colegiatura?"
        │
        ▼
┌─────────────────┐
│ ChatAgent       │──► Detecta intención fiscal
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ FiscalAdvisorAgent      │──► Recupera chunks relevantes de biblioteca fiscal
│ (con RAG)               │
└────────┬────────────────┘
         │
         ▼
┌─────────────────┐
│ ChatAgent       │──► Formatea respuesta amigable
└─────────────────┘
```

## Estructura de código

```
backend/app/agents/
├── __init__.py
├── base.py              # Agent, AgentResult, AgentContext
├── config.py            # Modelos por agente, temperaturas, max_tokens
├── orchestrator.py      # OrchestratorAgent
├── ocr_agent.py         # OCRAgent
├── chat_agent.py        # ChatAgent
├── validator_agent.py   # ValidatorAgent
├── billing_agent.py     # BillingAgent
├── librarian_agent.py   # LibrarianAgent
├── fiscal_agent.py      # FiscalAdvisorAgent + RAG
├── financial_agent.py   # FinancialAdvisorAgent + RAG
├── rag/                 # Motor de RAG simple
│   ├── __init__.py
│   └── simple_rag.py
└── tools/               # Herramientas que pueden usar los agentes
    ├── __init__.py
    └── db_tools.py
```

## Bibliotecas de conocimiento

Ubicadas en `docs/agents/` para que sean fáciles de editar sin tocar código.

```
docs/agents/
├── fiscal_library/              # RAG del FiscalAdvisorAgent
│   ├── 00_intro.md
│   ├── 01_regimenes_fiscales.md
│   ├── 02_deducciones_personales.md
│   ├── 03_contabilidad_pymes.md
│   ├── 04_facturacion_electronica.md
│   └── 05_obligaciones_sat.md
├── financial_library/           # RAG del FinancialAdvisorAgent
│   ├── 00_intro.md
│   ├── 01_ahro_personal.md
│   ├── 02_presupuesto_hogar.md
│   ├── 03_gastos_discrecionales.md
│   ├── 04_inversion_basica.md
│   └── 05_optimizacion_gastos.md
└── prompts/                     # Prompts versionados por agente
    ├── orchestrator_system.md
    ├── ocr_system.md
    └── ...
```

### Reglas para el contenido de bibliotecas

- Cada archivo MD debe ser factual y citar fuentes cuando sea posible.
- Los especialistas fiscal/financiero deben responder siempre con una **advertencia estándar** cuando el tema requiera validación profesional.
- El contenido se indexa al iniciar el sistema (embeddings) o se busca por palabras clave si no hay vector DB.

## Seguridad y limitaciones

- Ningún agente puede revelar claves API, tokens, arquitectura interna ni datos de otros usuarios.
- Los agentes fiscales/financieros no dan consejo legal ni contable definitivo; siempre recomiendan consultar a un profesional.
- Cada llamada a agente se registra en `PipelineTrace` para auditoría.

## Modelos y OpenRouter

Configuración por defecto (ajustable en `.env`):

| Rol | Modelo OpenRouter | Razón |
|-----|-------------------|-------|
| Obreros | `deepseek/deepseek-chat` | Barato, rápido, bueno para tareas estructuradas |
| Especialistas | `deepseek/deepseek-chat` o `anthropic/claude-3.5-sonnet` | Mayor precisión en temas complejos |

Variables de entorno:

```bash
OPENROUTER_API_KEY=sk-or-v1-...
AGENT_WORKER_MODEL=deepseek/deepseek-chat
AGENT_SPECIALIST_MODEL=deepseek/deepseek-chat
```

## Integración progresiva

1. **P0:** Implementar `OrchestratorAgent`, `OCRAgent` y `ChatAgent`.
2. **P1:** Agregar `ValidatorAgent`, `BillingAgent` y `LibrarianAgent`.
3. **P2:** Agregar `FiscalAdvisorAgent` y `FinancialAdvisorAgent` con RAG.
4. **P3:** Reemplazar llamadas directas a LLM en los módulos legacy por agentes.

## Nota importante

> Esta arquitectura se implementa de forma incremental. Los módulos existentes (`ocr/service.py`, `chat/service.py`, etc.) siguen funcionando mientras se migra funcionalidad a los agentes.
