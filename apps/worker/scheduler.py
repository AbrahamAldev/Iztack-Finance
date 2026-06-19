"""
ARQ Scheduler - Tareas periódicas programadas.
Reemplaza Celery Beat. Se ejecuta como proceso separado.
"""
import asyncio
import logging
from datetime import datetime, time

from arq import create_pool
from arq.connections import RedisSettings

logger = logging.getLogger("scheduler")


class Scheduler:
    """Programador de tareas periódicas usando Redis."""

    def __init__(self):
        self.settings = RedisSettings(
            host="localhost",
            port=6379,
            database=0,
        )
        self.tasks = [
            # (nombre, función, cron_expresión)
            # Diarias
            {"name": "retention_purge", "hour": 3, "minute": 0, "func": "retention_purge"},
            {"name": "quota_check", "hour": None, "minute": None, "interval_hours": 6, "func": "quota_check"},
            
            # Mensuales (día 1)
            {"name": "monthly_email", "day": 1, "hour": 8, "minute": 0, "func": "monthly_email"},
            
            # Continuas (cada hora en horario laboral)
            {"name": "update_analytics", "hour": 22, "minute": 0, "func": "update_analytics"},
        ]

    async def run_forever(self):
        """Loop principal del scheduler."""
        logger.info("🕐 Scheduler iniciado")
        
        while True:
            now = datetime.now()
            
            for task in self.tasks:
                should_run = False
                
                if "interval_hours" in task:
                    # Tarea por intervalo (ej: cada 6h)
                    if now.hour % task["interval_hours"] == 0 and now.minute == 0:
                        should_run = True
                elif "day" in task:
                    # Tarea mensual (día específico)
                    if now.day == task["day"] and now.hour == task["hour"] and now.minute == task["minute"]:
                        should_run = True
                else:
                    # Tarea diaria
                    if now.hour == task["hour"] and now.minute == task["minute"]:
                        should_run = True
                
                if should_run:
                    await self._enqueue_task(task)
            
            # Esperar 30 segundos antes de checkear de nuevo
            await asyncio.sleep(30)

    async def _enqueue_task(self, task: dict):
        """Agendar una tarea en Redis."""
        try:
            pool = await create_pool(self.settings)
            job = await pool.enqueue_job(
                task["func"],
                _queue="housekeeping",
            )
            await pool.close()
            logger.info(f"✅ Task scheduled: {task['name']} (job: {job.job_id})")
        except Exception as e:
            logger.error(f"❌ Failed to schedule {task['name']}: {e}")


if __name__ == "__main__":
    scheduler = Scheduler()
    asyncio.run(scheduler.run_forever())