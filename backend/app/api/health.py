"""Health check API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings, Settings
from app.models.database import get_db

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check():
    """Basic health check endpoint."""
    settings = get_settings()
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/health/db", tags=["health"])
async def health_check_db(db: AsyncSession = Depends(get_db)):
    """Database connectivity health check."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}