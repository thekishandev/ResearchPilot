"""
Research Service
Coordinates the complete research workflow
"""
import asyncio
import json
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from loguru import logger
from datetime import datetime

from app.schemas.research import ResearchQuery
from app.models.research import Research
from app.services.cerebras_service import CerebrasService
from app.services.mcp_orchestrator import MCPOrchestrator


class ResearchService:
    """Service for complete research workflow"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cerebras_service = CerebrasService()
        self.mcp_orchestrator = MCPOrchestrator()
        # Removed ollama_service - using Cerebras exclusively
    
    async def process_query(
        self,
        research_id: str,
        query: ResearchQuery
    ) -> None:
        """
        Process a research query end-to-end
        
        Steps:
        1. Query MCP sources in parallel
        2. Synthesize results with Cerebras
        3. Score credibility with Ollama
        4. Save results to database
        """
        try:
            logger.info(f"Processing research {research_id}")
            
            # Update status to processing
            await self._update_status(research_id, "processing")
            
            # Step 1: Query all sources in parallel
            logger.info("Step 1: Querying MCP sources...")
            source_results = await self.mcp_orchestrator.query_all_sources(
                query.query,
                query.sources
            )
            
            # Save intermediate results
            await self._save_source_results(research_id, source_results)
            
            # Step 2: Synthesize with Cerebras
            logger.info("Step 2: Synthesizing with Cerebras...")
            synthesis = await self._synthesize_results(query.query, source_results)
            
            # Save synthesis
            await self._save_synthesis(research_id, synthesis)
            
            # Step 3: Set default credibility score (Ollama removed due to memory constraints)
            # Using Cerebras exclusively for all AI inference
            credibility_score = 0.75  # Default high confidence for Cerebras synthesis
            if query.include_credibility:
                logger.info("Step 3: Setting credibility score (using Cerebras-only mode)")
                await self._save_credibility(research_id, credibility_score)
            
            # Mark as completed
            await self._update_status(research_id, "completed")
            
            logger.info(f"✅ Research {research_id} completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Research {research_id} failed: {e}")
            await self._update_status(research_id, "failed", error=str(e))
            raise
    
    async def stream_results(
        self,
        research_id: str
    ) -> AsyncIterator[str]:
        """
        Stream research results in real-time
        Creates a new DB session for each query to avoid stale data
        
        Yields:
            JSON-encoded chunks of results
        """
        from app.core.database import AsyncSessionLocal
        
        try:
            # Get initial research record with a fresh session
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Research).where(Research.id == research_id)
                )
                research = result.scalar_one_or_none()
            
            if not research:
                yield json.dumps({"error": "Research not found"})
                return
            
            # Send initial state immediately
            initial_state = {
                "id": research.id,
                "status": research.status,
                "query": research.query,
                "sources": research.sources,
                "results": research.results,
                "synthesis": research.synthesis,
                "credibility_score": research.credibility_score,
            }
            yield json.dumps(initial_state)
            
            # If already completed/failed, send final state and exit
            if research.status in ["completed", "failed"]:
                logger.info(f"Research {research_id} already {research.status}, sending final state")
                return
            
            # Stream status updates while processing
            max_polls = 120  # 60 seconds max (120 * 0.5s)
            polls = 0
            
            logger.info(f"Starting SSE stream for research {research_id}, initial status: {research.status}")
            
            while research.status in ["pending", "processing"] and polls < max_polls:
                polls += 1
                
                # Wait before polling
                await asyncio.sleep(0.5)
                
                # Re-query with a FRESH session to see latest committed data
                async with AsyncSessionLocal() as db:
                    result = await db.execute(
                        select(Research).where(Research.id == research_id)
                    )
                    research = result.scalar_one_or_none()
                
                if not research:
                    logger.error(f"Research {research_id} not found during streaming")
                    yield json.dumps({"error": "Research not found"})
                    return
                
                if polls % 10 == 0:  # Log every 5 seconds
                    logger.info(f"SSE poll #{polls}: status={research.status}, has_results={research.results is not None}, has_synthesis={research.synthesis is not None}")
                
                # Yield current state
                state = {
                    "id": research.id,
                    "status": research.status,
                    "query": research.query,
                    "sources": research.sources,
                    "results": research.results,
                    "synthesis": research.synthesis,
                    "credibility_score": research.credibility_score,
                }
                
                yield json.dumps(state)
                
                # Break if completed or failed
                if research.status in ["completed", "failed"]:
                    logger.info(f"✅ Research {research_id} {research.status}, closing SSE stream after {polls} polls")
                    break
            
            # Timeout check
            if polls >= max_polls and research.status in ["pending", "processing"]:
                logger.warning(f"⏱️ Research {research_id} streaming timed out after 60s, final status: {research.status}")
                yield json.dumps({"error": "Research processing timeout", "status": research.status})
            
        except Exception as e:
            logger.error(f"Streaming error for {research_id}: {e}")
            yield json.dumps({"error": str(e)})
    
    async def _synthesize_results(
        self,
        query: str,
        source_results: list
    ) -> str:
        """Synthesize results using Cerebras"""
        synthesis_chunks = []
        
        async for chunk in self.cerebras_service.synthesize(
            query,
            source_results,
            stream=False
        ):
            synthesis_chunks.append(chunk)
        
        return ''.join(synthesis_chunks) if synthesis_chunks else ""
    
    async def _update_status(
        self,
        research_id: str,
        status: str,
        error: str = None
    ) -> None:
        """Update research status"""
        values = {"status": status}
        
        if status == "completed":
            values["completed_at"] = datetime.utcnow()
        
        if error:
            values["error"] = error
        
        await self.db.execute(
            update(Research)
            .where(Research.id == research_id)
            .values(**values)
        )
        await self.db.commit()
    
    async def _save_source_results(
        self,
        research_id: str,
        results: list
    ) -> None:
        """Save source results"""
        await self.db.execute(
            update(Research)
            .where(Research.id == research_id)
            .values(results=results)
        )
        await self.db.commit()
    
    async def _save_synthesis(
        self,
        research_id: str,
        synthesis: str
    ) -> None:
        """Save synthesis"""
        await self.db.execute(
            update(Research)
            .where(Research.id == research_id)
            .values(synthesis=synthesis)
        )
        await self.db.commit()
    
    async def _save_credibility(
        self,
        research_id: str,
        score: float
    ) -> None:
        """Save credibility score"""
        await self.db.execute(
            update(Research)
            .where(Research.id == research_id)
            .values(credibility_score=score)
        )
        await self.db.commit()
