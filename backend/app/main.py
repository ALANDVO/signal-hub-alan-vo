"""
signal-hub-alan-vo: PHP Interpreter Issue Analysis Platform

AI/ML developer tool for analyzing PHP interpreter issues including
JIT segmentation faults, GC performance regressions, fork safety issues,
and array_unique bugs.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, issues
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="signal-hub-alan-vo",
    description="PHP Interpreter Issue Analysis Platform - AI/ML developer tools for PHP core issues",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(issues.router, prefix="/api/v1", tags=["issues"])


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "signal-hub-alan-vo",
        "description": "PHP Interpreter Issue Analysis Platform",
        "version": "1.0.0",
        "author": "Alan Vo <alanvo@gmail.com>",
        "docs": "/docs",
    }