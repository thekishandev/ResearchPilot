"""
API Router - Version 1
"""
from fastapi import APIRouter

from app.api.v1.endpoints import research, sources, health

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
