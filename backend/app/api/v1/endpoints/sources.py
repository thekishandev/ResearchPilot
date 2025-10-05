"""
Sources endpoint - MCP source management and health checks
"""
from fastapi import APIRouter, HTTPException
from loguru import logger
from typing import List

from app.schemas.sources import SourceStatus, SourceHealth
from app.services.mcp_orchestrator import MCPOrchestrator

router = APIRouter()


@router.get("/status", response_model=List[SourceStatus])
async def get_sources_status():
    """
    Get the status of all MCP sources
    """
    try:
        orchestrator = MCPOrchestrator()
        sources = await orchestrator.check_all_sources()
        
        return [
            SourceStatus(
                name=source["name"],
                status=source["status"],
                response_time=source.get("response_time"),
                last_check=source.get("last_check"),
            )
            for source in sources
        ]
    except Exception as e:
        logger.error(f"Error checking source status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=SourceHealth)
async def get_sources_health():
    """
    Get overall health of MCP sources
    """
    try:
        orchestrator = MCPOrchestrator()
        health = await orchestrator.get_health_summary()
        
        return SourceHealth(
            total_sources=health["total"],
            healthy_sources=health["healthy"],
            unhealthy_sources=health["unhealthy"],
            health_percentage=health["percentage"],
        )
    except Exception as e:
        logger.error(f"Error getting source health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{source_name}/status", response_model=SourceStatus)
async def get_source_status(source_name: str):
    """
    Get the status of a specific MCP source
    """
    try:
        orchestrator = MCPOrchestrator()
        source = await orchestrator.check_source(source_name)
        
        if not source:
            raise HTTPException(status_code=404, detail=f"Source '{source_name}' not found")
        
        return SourceStatus(
            name=source["name"],
            status=source["status"],
            response_time=source.get("response_time"),
            last_check=source.get("last_check"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking source {source_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
