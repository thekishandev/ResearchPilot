"""
Research endpoint - Main research query processing
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from typing import Optional
import asyncio

from app.core.database import get_db
from app.schemas.research import ResearchQuery, ResearchResponse, ResearchStatus
from app.services.cerebras_service import CerebrasService
from app.services.mcp_orchestrator import MCPOrchestrator
from app.services.ollama_service import OllamaService
from app.core.monitoring import research_queries_total, research_query_duration_seconds
from time import time

router = APIRouter()


@router.post("/query", response_model=ResearchResponse)
async def create_research_query(
    query: ResearchQuery,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a research query for processing
    Returns a research ID for tracking
    """
    start_time = time()
    
    try:
        logger.info(f"Received research query: {query.query[:100]}...")
        
        # Initialize services
        cerebras_service = CerebrasService()
        mcp_orchestrator = MCPOrchestrator()
        
        # Validate query
        if len(query.query) < 10:
            raise HTTPException(status_code=400, detail="Query too short (minimum 10 characters)")
        
        # Create research record in database
        from app.models.research import Research
        research = Research(
            query=query.query,
            sources=query.sources or [],
            status="processing",
        )
        db.add(research)
        await db.commit()
        await db.refresh(research)
        
        # Start async processing (without passing the session)
        asyncio.create_task(process_research_query(research.id, query))
        
        # Record metrics
        research_queries_total.inc()
        duration = time() - start_time
        research_query_duration_seconds.observe(duration)
        
        logger.info(f"Research query created with ID: {research.id}")
        
        return ResearchResponse(
            id=research.id,
            status="processing",
            message="Research query submitted successfully",
        )
        
    except Exception as e:
        logger.error(f"Error creating research query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/{research_id}")
async def stream_research_results(
    research_id: str,
    request: Request
):
    """
    Stream research results in real-time using SSE
    Creates its own database session for long-running streaming
    """
    from app.services.research_service import ResearchService
    from app.core.database import AsyncSessionLocal
    
    async def event_generator():
        """Generate SSE events"""
        try:
            research_service = ResearchService(None)  # Will create session per query
            async for chunk in research_service.stream_results(research_id):
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.01)  # Small delay for smooth streaming
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/{research_id}", response_model=ResearchStatus)
async def get_research_status(
    research_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the status and results of a research query
    """
    from app.models.research import Research
    from sqlalchemy import select
    
    try:
        result = await db.execute(select(Research).where(Research.id == research_id))
        research = result.scalar_one_or_none()
        
        if not research:
            raise HTTPException(status_code=404, detail="Research not found")
        
        return ResearchStatus(
            id=research.id,
            status=research.status,
            query=research.query,
            sources=research.sources,
            results=research.results,
            synthesis=research.synthesis,
            credibility_score=research.credibility_score,
            created_at=research.created_at,
            completed_at=research.completed_at,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{research_id}")
async def delete_research(
    research_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a research query and its results
    """
    from app.models.research import Research
    from sqlalchemy import select, delete
    
    try:
        result = await db.execute(select(Research).where(Research.id == research_id))
        research = result.scalar_one_or_none()
        
        if not research:
            raise HTTPException(status_code=404, detail="Research not found")
        
        await db.execute(delete(Research).where(Research.id == research_id))
        await db.commit()
        
        return {"message": "Research deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_research_query(
    research_id: str,
    query: ResearchQuery
):
    """
    Background task to process research query
    Creates its own database session to avoid transaction conflicts
    """
    from app.services.research_service import ResearchService
    from app.core.database import AsyncSessionLocal
    
    # Create a new database session for this background task
    async with AsyncSessionLocal() as db:
        try:
            research_service = ResearchService(db)
            await research_service.process_query(research_id, query)
            logger.info(f"Research {research_id} completed successfully")
        except Exception as e:
            logger.error(f"Error processing research {research_id}: {e}")
            # Update research status to failed
            from app.models.research import Research
            from sqlalchemy import update
            
            try:
                await db.execute(
                    update(Research)
                    .where(Research.id == research_id)
                    .values(status="failed", error=str(e))
                )
                await db.commit()
            except Exception as update_error:
                logger.error(f"Failed to update error status: {update_error}")


@router.get("/history", response_model=list[ResearchResponse])
async def get_research_history(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Get research history (recent queries)
    """
    try:
        from app.models.research import Research
        from sqlalchemy import select, desc
        
        # Query recent research entries
        result = await db.execute(
            select(Research)
            .order_by(desc(Research.created_at))
            .limit(limit)
            .offset(offset)
        )
        research_items = result.scalars().all()
        
        return [
            ResearchResponse(
                id=str(item.id),
                status=item.status,
                query=item.query
            )
            for item in research_items
        ]
        
    except Exception as e:
        logger.error(f"Error fetching research history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch research history")

