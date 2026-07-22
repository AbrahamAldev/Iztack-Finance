"""
Iztack-Finance - Fiscal Routes (Módulo Fiscal México)
CSF upload, tax regime management, deduction analysis.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.modules.auth.deps import get_current_user
from app.modules.fiscal.service import FiscalService
from app.database.models import User

router = APIRouter(prefix="/api/fiscal", tags=["Fiscal"])


@router.get("/data")
async def get_fiscal_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get stored fiscal data for the current user."""
    service = FiscalService(db)
    data = await service.get_fiscal_data(current_user.id)
    return {"fiscal_data": data}


@router.put("/data")
async def save_fiscal_data(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save fiscal data (RFC, régimen, razón social, etc.)."""
    service = FiscalService(db)
    result = await service.save_fiscal_data(current_user.id, data)
    return {"success": True, "fiscal_data": result}


@router.post("/csf/upload")
async def upload_csf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload Constancia de Situación Fiscal (PDF) and extract data."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Archivo muy grande. Máximo 5MB.")

    service = FiscalService(db)
    result = await service.process_csf(current_user.id, contents)
    return result


@router.get("/deductions")
async def get_deductions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get deduction recommendations based on fiscal regime."""
    service = FiscalService(db)
    deductions = await service.get_deduction_recommendations(current_user.id)
    return {"deductions": deductions}