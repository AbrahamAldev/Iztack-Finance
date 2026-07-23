"""
Iztack-Finance - Monitoring API Routes
Admin endpoints for sensors, metrics, pipeline traces, and logs.
Protected by staff JWT (admfinance.iztack.com).
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.modules.admin_staff.routes import get_staff_token
from app.modules.monitoring.service import SensorsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["monitoring"])


def get_sensors_service(db: AsyncSession = Depends(get_db)) -> SensorsService:
    return SensorsService(db)


@router.post("/sensors/run", summary="Run all sensor checks now")
async def run_sensors(
    svc: SensorsService = Depends(get_sensors_service),
    payload: dict = Depends(get_staff_token),
):
    try:
        result = await svc.run_all_checks()
        return result
    except Exception as exc:
        logger.error(f"Error running sensors: {exc}")
        raise HTTPException(status_code=500, detail=f"Sensor run failed: {exc}")


@router.get("/sensors", summary="Get latest sensor reading per component")
async def get_latest_sensors(
    svc: SensorsService = Depends(get_sensors_service),
    payload: dict = Depends(get_staff_token),
):
    return await svc.get_latest_by_component()


@router.get("/sensors/history", summary="Get recent sensor readings")
async def get_sensor_history(
    minutes: int = Query(60, ge=1, le=10080),
    svc: SensorsService = Depends(get_sensors_service),
    payload: dict = Depends(get_staff_token),
):
    return await svc.get_recent_readings(minutes=minutes)


@router.get("/pipeline", summary="Get recent pipeline traces")
async def get_pipeline_traces(
    limit: int = Query(50, ge=1, le=500),
    svc: SensorsService = Depends(get_sensors_service),
    payload: dict = Depends(get_staff_token),
):
    return await svc.get_pipeline_traces(limit=limit)


@router.get("/metrics", summary="Get key system metrics")
async def get_metrics(
    svc: SensorsService = Depends(get_sensors_service),
    payload: dict = Depends(get_staff_token),
):
    return await svc.get_metrics()


@router.get("/logs", summary="Get aggregated monitoring data")
async def get_logs(
    svc: SensorsService = Depends(get_sensors_service),
    payload: dict = Depends(get_staff_token),
):
    return {
        "sensors": await svc.get_latest_by_component(),
        "metrics": await svc.get_metrics(),
        "traces": await svc.get_pipeline_traces(limit=20),
    }
