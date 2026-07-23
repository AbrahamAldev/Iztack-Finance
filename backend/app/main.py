"""
Sistema Financiero - Main Application Entry Point
FastAPI application with CORS, middleware, and route registration.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database.connection import close_db, init_db
from app.modules.admin_staff.routes import router as admin_router
from app.modules.agents.routes import router as agents_router
from app.modules.almacenamiento.routes import router as almacenamiento_router
from app.modules.auth.routes import router as auth_router
from app.modules.business.routes import router as business_router
from app.modules.chat.routes import router as chat_router
from app.modules.clasificacion.routes import router as clasificacion_router
from app.modules.dashboard.routes import router as dashboard_router
from app.modules.finanzas.routes import router as finanzas_router
from app.modules.fiscal.routes import router as fiscal_router
from app.modules.garantias.routes import router as garantias_router
from app.modules.info import router as info_router
from app.modules.monitoring.routes import router as monitoring_router
from app.modules.ocr.routes import router as ocr_router
from app.modules.settings.routes import router as settings_router
from app.modules.setup.routes import router as setup_router
from app.modules.shopping_list.routes import router as shopping_list_router
from app.modules.tickets.routes import router as tickets_router
from app.scheduler import start_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}...")
    logger.info(f"Environment: {settings.environment}")

    # Initialize database
    await init_db()
    logger.info("Database initialized successfully")

    # Start scheduler
    start_scheduler()
    logger.info("Scheduler started")

    yield

    # Shutdown
    stop_scheduler()
    await close_db()
    logger.info("Database connections closed")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema Automatizado de Gestión de Tickets, Facturas y Finanzas Personales",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.environment == "development" else None,
    redoc_url="/api/redoc" if settings.environment == "development" else None,
)

# CORS middleware
_origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
if settings.environment == "development":
    _origins.append("http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Health Check
# =============================================================================

@app.get("/api/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


# =============================================================================
# Route Registration
# =============================================================================

app.include_router(ocr_router, prefix="/api/ocr", tags=["OCR"])
app.include_router(setup_router, prefix="/api/setup", tags=["Setup"])
app.include_router(info_router, prefix="/api", tags=["System"])
app.include_router(auth_router, tags=["Auth"])
app.include_router(settings_router, tags=["Settings"])
app.include_router(tickets_router, tags=["Tickets"])
app.include_router(chat_router, tags=["Chat"])
app.include_router(dashboard_router, tags=["Dashboard"])
app.include_router(admin_router, tags=["Admin"])
app.include_router(business_router, tags=["Business"])
app.include_router(fiscal_router, prefix="/api/fiscal", tags=["Fiscal"])
app.include_router(finanzas_router)
app.include_router(garantias_router)
app.include_router(shopping_list_router)
app.include_router(almacenamiento_router)
app.include_router(clasificacion_router)
app.include_router(agents_router)
app.include_router(monitoring_router, prefix="/api", tags=["Monitoring"])

# Future modules (to be activated in subsequent phases):
# from app.modules.bots.routes import router as bots_router
# from app.modules.facturacion.routes import router as facturacion_router
# app.include_router(bots_router, prefix="/api/bots", tags=["Bots"])
# app.include_router(facturacion_router, prefix="/api/facturacion", tags=["Facturación"])


@app.get("/", tags=["System"])
async def root():
    """Root endpoint - API information."""
    return {
        "message": f"Bienvenido a {settings.app_name}",
        "version": settings.app_version,
        "docs": "/api/docs",
        "health": "/api/health",
    }
