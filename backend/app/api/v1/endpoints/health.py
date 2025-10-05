"""
Health endpoint - System health checks
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from loguru import logger
import aiohttp

from app.core.database import get_db
from app.core.config import settings
from app.schemas.health import HealthCheck, ComponentHealth

router = APIRouter()


@router.get("", response_model=HealthCheck)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check for all system components
    """
    health_status = {
        "status": "healthy",
        "components": {}
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health_status["components"]["database"] = ComponentHealth(
            status="healthy",
            message="Database connection successful"
        )
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["components"]["database"] = ComponentHealth(
            status="unhealthy",
            message=f"Database error: {str(e)}"
        )
        health_status["status"] = "unhealthy"
    
    # Check MCP Gateway
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{settings.MCP_GATEWAY_URL}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    health_status["components"]["mcp_gateway"] = ComponentHealth(
                        status="healthy",
                        message="MCP Gateway operational"
                    )
                else:
                    health_status["components"]["mcp_gateway"] = ComponentHealth(
                        status="degraded",
                        message=f"MCP Gateway returned status {response.status}"
                    )
    except Exception as e:
        logger.error(f"MCP Gateway health check failed: {e}")
        health_status["components"]["mcp_gateway"] = ComponentHealth(
            status="unhealthy",
            message=f"MCP Gateway error: {str(e)}"
        )
    
    # Check Ollama
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{settings.OLLAMA_HOST}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    health_status["components"]["ollama"] = ComponentHealth(
                        status="healthy",
                        message="Ollama operational"
                    )
                else:
                    health_status["components"]["ollama"] = ComponentHealth(
                        status="degraded",
                        message=f"Ollama returned status {response.status}"
                    )
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        health_status["components"]["ollama"] = ComponentHealth(
            status="unhealthy",
            message=f"Ollama error: {str(e)}"
        )
    
    # Check Cerebras API
    health_status["components"]["cerebras"] = ComponentHealth(
        status="healthy" if settings.CEREBRAS_API_KEY else "unconfigured",
        message="Cerebras API key configured" if settings.CEREBRAS_API_KEY else "Cerebras API key not configured"
    )
    
    return HealthCheck(**health_status)
