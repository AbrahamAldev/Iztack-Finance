import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import User
from app.modules.almacenamiento.local_storage import (
    LocalStorageService,
    QuotaExceededError,
    FileNotFoundError_,
)
from app.modules.auth.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/storage", tags=["Storage"])


def _get_storage(user_id: str) -> LocalStorageService:
    return LocalStorageService(user_id)


@router.get("/usage")
async def get_storage_usage(
    current_user: User = Depends(get_current_user),
):
    svc = _get_storage(current_user.id)
    usage = svc.get_usage()
    return {
        "used_bytes": usage["used_bytes"],
        "max_bytes": usage["max_bytes"],
        "used_pct": usage["used_pct"],
        "free_bytes": usage["free_bytes"],
    }


@router.get("/files")
async def list_files(
    file_type: Optional[str] = Query(None, alias="type"),
    current_user: User = Depends(get_current_user),
):
    svc = _get_storage(current_user.id)
    if file_type == "tickets":
        files = svc.list_tickets()
    elif file_type == "invoices":
        files = svc.list_invoices()
    else:
        files = svc.list_all()
    return {"files": files, "total": len(files)}


@router.get("/files/{file_id}")
async def get_file_metadata(
    file_id: str,
    current_user: User = Depends(get_current_user),
):
    svc = _get_storage(current_user.id)
    for f in svc.list_all():
        if f["id"] == file_id:
            return f
    raise HTTPException(status_code=404, detail="Archivo no encontrado")


@router.get("/files/{file_id}/download")
async def download_file(
    file_id: str,
    variant: str = Query("original"),
    current_user: User = Depends(get_current_user),
):
    svc = _get_storage(current_user.id)

    ticket_dir = svc.tickets_dir / file_id
    inv_dir = svc.invoices_dir / file_id

    if ticket_dir.exists():
        if variant == "original":
            path = ticket_dir / "original.jpg"
        elif variant == "processed":
            path = ticket_dir / "processed.jpg"
        else:
            raise HTTPException(status_code=400, detail="Variante inválida")
        if not path.exists():
            raise HTTPException(status_code=404, detail="Imagen no encontrada")
        return FileResponse(str(path), media_type="image/jpeg", filename=f"{file_id}_{variant}.jpg")

    if inv_dir.exists():
        if variant == "pdf":
            path = inv_dir / "factura.pdf"
        elif variant == "xml":
            path = inv_dir / "factura.xml"
        else:
            raise HTTPException(status_code=400, detail="Variante inválida")
        if not path.exists():
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        mime = "application/pdf" if variant == "pdf" else "text/xml"
        return FileResponse(str(path), media_type=mime, filename=f"factura_{file_id}.{variant}")

    raise HTTPException(status_code=404, detail="Archivo no encontrado")


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
):
    svc = _get_storage(current_user.id)
    ok = svc.delete_by_id(file_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return {"success": True, "message": "Archivo eliminado"}
