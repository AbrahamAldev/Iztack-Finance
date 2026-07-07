"""
Sistema Financiero - Main Application Entry Point
FastAPI application with CORS, middleware, and route registration.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.database.connection import init_db, close_db

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
    
    yield
    
    # Shutdown
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else [
        "http://localhost:3000",
        "https://tu-dominio.com",
    ],
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

from app.modules.ocr.routes import router as ocr_router
from app.modules.setup.routes import router as setup_router
from app.modules.info import router as info_router
from app.modules.auth.routes import router as auth_router

app.include_router(ocr_router, prefix="/api/ocr", tags=["OCR"])
app.include_router(setup_router, prefix="/api/setup", tags=["Setup"])
app.include_router(info_router, prefix="/api", tags=["System"])
app.include_router(auth_router, tags=["Auth"])

# Future modules (to be activated in subsequent phases):
# from app.modules.bots.routes import router as bots_router
# from app.modules.facturacion.routes import router as facturacion_router
# from app.modules.finanzas.routes import router as finanzas_router
# from app.modules.shopping_list.routes import router as shopping_list_router
# from app.modules.almacenamiento.routes import router as almacenamiento_router
# app.include_router(bots_router, prefix="/api/bots", tags=["Bots"])
# app.include_router(facturacion_router, prefix="/api/facturacion", tags=["Facturación"])
# app.include_router(finanzas_router, prefix="/api/finanzas", tags=["Finanzas"])
# app.include_router(shopping_list_router, prefix="/api/shopping-list", tags=["Lista de Compras"])
# app.include_router(almacenamiento_router, prefix="/api/almacenamiento", tags=["Almacenamiento"])


@app.get("/", tags=["System"])
async def root():
    """Root endpoint - API information."""
    return {
        "message": f"Bienvenido a {settings.app_name}",
        "version": settings.app_version,
        "docs": "/api/docs",
        "health": "/api/health",
    }