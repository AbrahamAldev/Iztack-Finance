"""
ARQ Worker - Sistema de procesamiento asíncrono
Reemplaza a Celery. Usa Redis como broker nativo.
Colas: ocr (alta), cfdi (media), housekeeping (baja)
"""
import asyncio
import logging
from typing import Optional
from datetime import datetime

from arq import create_pool
from arq.connections import RedisSettings
from arq.worker import Worker, WorkerSettings

from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

settings = get_settings()


# =============================================================================
# Tareas OCR
# =============================================================================

async def process_ocr(ctx, ticket_id: str) -> dict:
    """Procesar OCR de un ticket: Tesseract → OpenRouter fallback."""
    logger.info(f"[ocr] Procesando ticket {ticket_id}")
    
    from packages.ocr.engines.tesseract import TesseractEngine
    from packages.ocr.engines.openrouter import OpenRouterEngine
    from packages.ocr.parsers.ticket_mx import TicketParser
    
    # 1. Tesseract primero
    tesseract = TesseractEngine()
    result = await tesseract.extract(ticket_id)
    
    # 2. Si confianza baja, fallback a OpenRouter
    if result.confidence < 0.75:
        logger.info(f"[ocr] Confianza baja ({result.confidence}), usando OpenRouter")
        openrouter = OpenRouterEngine()
        result = await openrouter.extract(ticket_id)
    
    # 3. Parsear resultado
    parser = TicketParser()
    parsed = parser.parse(result.raw_text)
    
    # 4. Guardar en DB
    # TODO: Update ticket status in DB
    
    return {
        "ticket_id": ticket_id,
        "confidence": result.confidence,
        "engine": result.engine,
        "parsed": parsed.dict(),
    }


async def process_cfdi(ctx, ticket_id: str) -> dict:
    """Solicitar CFDI en el portal correspondiente."""
    logger.info(f"[cfdi] Facturando ticket {ticket_id}")
    
    from app.modules.facturacion.portales import PortalFactory
    
    # TODO: Obtener ticket data de DB
    # TODO: Obtener credenciales de DB
    # TODO: Ejecutar adapter
    
    return {"ticket_id": ticket_id, "status": "pending"}


async def sync_cloud(ctx, ticket_id: str) -> dict:
    """Sincronizar archivos a la nube personal del usuario."""
    logger.info(f"[cloud] Sincronizando ticket {ticket_id}")
    
    from packages.storage.cloud import get_cloud_client
    from packages.storage.local import LocalStorage
    
    # TODO: Obtener cloud_provider del household
    # TODO: Subir archivos
    
    return {"ticket_id": ticket_id, "synced": True}


async def monthly_email(ctx) -> dict:
    """Enviar ZIP mensual por correo (día 1 del mes)."""
    logger.info("[email] Generando reporte mensual...")
    
    from packages.storage.email_storage import EmailStorage
    
    email = EmailStorage()
    result = await email.send_monthly_report()
    
    return {"sent": result.success, "files": result.file_count}


async def retention_purge(ctx) -> dict:
    """Purgar archivos locales > 13 meses."""
    logger.info("[retention] Purgando archivos antiguos...")
    
    from packages.storage.retention import RetentionManager
    
    retention = RetentionManager()
    result = await retention.purge_old_files(max_age_months=13)
    
    return {"purged": result.purged_count, "errors": result.error_count}


async def quota_check(ctx) -> dict:
    """Verificar cuota de nube personal cada 6h."""
    logger.info("[quota] Verificando cuota de nube...")
    
    from packages.storage.cloud import get_cloud_client
    
    # TODO: Iterar households con cloud_provider
    # TODO: Verificar cuota
    
    return {"checked": True}


async def update_analytics(ctx, household_id: str) -> dict:
    """Recalcular análisis financiero y sugerencias."""
    logger.info(f"[analytics] Actualizando análisis para {household_id}")
    
    from packages.analytics.consumption_cycle import ConsumptionCycleAnalyzer
    
    analyzer = ConsumptionCycleAnalyzer()
    result = await analyzer.analyze(household_id)
    
    return {"household_id": household_id, "cycles_updated": result}


# =============================================================================
# Configuración del Worker
# =============================================================================

WORKER_CONFIG = {
    "ocr": {
        "concurrency": 4,
        "timeout": 300,  # 5 min
    },
    "cfdi": {
        "concurrency": 2,  # Playwright pesa
        "timeout": 600,  # 10 min
    },
    "housekeeping": {
        "concurrency": 1,
        "timeout": 300,
    },
}


class WorkerSettings:
    """Configuración ARQ para el worker."""
    
    functions = [
        process_ocr,
        process_cfdi,
        sync_cloud,
        monthly_email,
        retention_purge,
        quota_check,
        update_analytics,
    ]
    
    redis_settings = RedisSettings(
        host=settings.redis_host or "localhost",
        port=6379,
        database=0,
    )
    
    keep_result = 3600  # 1 hora
    keep_result_forever = False
    job_timeout = 600  # 10 min max
    max_burst_jobs = 10
    
    # Colas con prioridad
    queue_class = "arq.connections.RedisQueue"
    
    on_startup = None
    on_shutdown = None
    after_job = None


# =============================================================================
# Función para agendar tareas desde la API
# =============================================================================

async def enqueue_ocr(ticket_id: str) -> Optional[str]:
    """Agendar OCR para un ticket."""
    pool = await create_pool(WorkerSettings.redis_settings)
    job = await pool.enqueue_job("process_ocr", ticket_id, _queue="ocr")
    await pool.close()
    return job.job_id if job else None


async def enqueue_cfdi(ticket_id: str) -> Optional[str]:
    """Agendar CFDI para un ticket."""
    pool = await create_pool(WorkerSettings.redis_settings)
    job = await pool.enqueue_job("process_cfdi", ticket_id, _queue="cfdi")
    await pool.close()
    return job.job_id if job else None


async def enqueue_cloud_sync(ticket_id: str) -> Optional[str]:
    """Agendar sync a nube."""
    pool = await create_pool(WorkerSettings.redis_settings)
    job = await pool.enqueue_job("sync_cloud", ticket_id, _queue="housekeeping")
    await pool.close()
    return job.job_id if job else None


# =============================================================================
# Entry point
# =============================================================================

if __name__ == "__main__":
    """Iniciar worker ARQ."""
    worker = Worker(WorkerSettings)
    asyncio.run(worker.run())