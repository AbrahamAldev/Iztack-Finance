"""
Iztack-Finance - Admin Staff Routes
API endpoints for admin portal (admfinance.iztack.com).
"""
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SyncSession
from app.database.models import StaffUser
from app.modules.admin_staff.service import AdminStaffService

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def get_staff_token(authorization: str = Header(None)) -> dict:
    """Verify staff JWT token from header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    token = authorization.split(" ")[1]
    payload = AdminStaffService.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return payload


def get_db():
    """Get sync DB session for admin endpoints."""
    db = SyncSession()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
async def register_admin(data: dict, db: Session = Depends(get_db)):
    """Register the first super_admin (admin@iztack.com only)."""
    try:
        service = AdminStaffService(db)
        user, token = await service.register_first_admin(
            email=data.get("email", ""),
            name=data.get("name", ""),
            password=data.get("password", ""),
        )
        return {
            "success": True,
            "access_token": token,
            "user": {"email": user.email, "name": user.name, "role": user.role},
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login_admin(data: dict, db: Session = Depends(get_db)):
    """Login staff user (must be @iztack.com)."""
    try:
        service = AdminStaffService(db)
        user, token = await service.login(
            email=data.get("email", ""),
            password=data.get("password", ""),
        )
        return {
            "success": True,
            "access_token": token,
            "user": {"email": user.email, "name": user.name, "role": user.role},
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/health")
async def admin_health(payload: dict = Depends(get_staff_token)):
    """Get system health (staff only)."""
    service = AdminStaffService(None)
    health = await service.get_health()
    return health


@router.get("/clients")
async def list_clients(payload: dict = Depends(get_staff_token), db: Session = Depends(get_db)):
    """List client users (staff only)."""
    if payload.get("role_level", 0) < 30:
        raise HTTPException(status_code=403, detail="Permiso insuficiente")
    service = AdminStaffService(db)
    clients = await service.get_clients_summary()
    return {"clients": clients}


@router.get("/staff")
async def list_staff(payload: dict = Depends(get_staff_token), db: Session = Depends(get_db)):
    """List staff users (admin+ only)."""
    if payload.get("role_level", 0) < 80:
        raise HTTPException(status_code=403, detail="Permiso insuficiente")
    service = AdminStaffService(db)
    staff = await service.get_staff_users()
    return {"staff": staff}


@router.put("/staff/{staff_id}/role")
async def update_staff_role(staff_id: str, data: dict, payload: dict = Depends(get_staff_token), db: Session = Depends(get_db)):
    """Update staff role (super_admin only)."""
    if payload.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Solo super_admin")
    try:
        service = AdminStaffService(db)
        user = await service.update_staff_role(
            staff_id=staff_id,
            role=data.get("role", "monitor"),
            role_level=data.get("role_level", 30),
            current_user=StaffUser(id=payload["sub"], role=payload["role"]),
        )
        return {"success": True, "user": {"email": user.email, "role": user.role}}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
