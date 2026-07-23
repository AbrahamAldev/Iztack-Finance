"""
Sistema Financiero - Database Connection Module
Async SQLAlchemy session management with PostgreSQL.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# Async engine (for FastAPI)
engine = create_async_engine(
    settings.database_url,
    echo=(settings.environment == "development"),
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync engine (for Telegram bot, scripts)
# Use psycopg v3 (already in requirements) instead of psycopg2.
_sync_db_url = settings.database_url.replace("+asyncpg", "+psycopg")
_sync_engine = create_engine(
    _sync_db_url,
    echo=False,
    pool_pre_ping=True,
)
SyncSession = sessionmaker(bind=_sync_engine, class_=Session)


def get_db_sync() -> Session:
    """Get a sync database session (for Telegram bot)."""
    db = SyncSession()
    try:
        return db
    except Exception:
        db.close()
        raise


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


async def get_db():
    """Dependency injection for database sessions."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connection."""
    await engine.dispose()
