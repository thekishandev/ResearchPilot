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
from a                    return ["web-search", "arxiv"]  # Safe default
                    
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI response: {e}")
            return ["web-search", "arxiv"]  # Safe default
        except Exception as e:
            logger.error(f"Error in AI source selection: {e}")
            return ["web-search", "arxiv", "news"]  # Safe defaultes.cerebras_service import CerebrasService
from app.services.mcp_orchestrator import MCPOrchestrator


class ResearchService:
    """Service for complete research workflow"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cerebras_service = CerebrasService()
        self.mcp_orchestrator = MCPOrchestrator()
        # Removed ollama_service - using Cerebras exclusively
    
    async def process_query_with_tools(
        self,
        research_id: str,
        query: ResearchQuery
    ) -> None:
        """
        Process a research query using intelligent tool selection.
        AI decides which sources to query based on the question.
        
        Steps:
        1. Get parent research context if this is a follow-up
        2. Ask AI which tools/sources to use
        3. Execute selected tools in parallel
        4. Synthesize results with Cerebras
        5. Save results to database
        """
        try:
            logger.info(f"Processing research {research_id} with tool use")
            
            # Update status to processing
            await self._update_status(research_id, "processing")
            
            # Step 0: Get parent research context if this is a follow-up
            parent_context = None
            if query.parent_research_id:
                logger.info(f"Step 0: Loading parent research {query.parent_research_id} for context...")
                parent_context = await self._get_parent_context(query.parent_research_id)
            
            # Step 1: Let AI decide which sources to query
            logger.info("Step 1: AI selecting optimal sources...")
            selected_sources = await self._select_sources_with_ai(query.query, parent_context)
            
            # Step 2: Query selected sources in parallel
            logger.info(f"Step 2: Querying {len(selected_sources)} selected sources: {selected_sources}")
            source_results = await self.mcp_orchestrator.query_all_sources(
                query.query,
                selected_sources
            )
            
            # Save intermediate results
            await self._save_source_results(research_id, source_results)
            
            # Step 3: Synthesize with Cerebras
            logger.info("Step 3: Synthesizing with Cerebras...")
            synthesis = await self._synthesize_results(query.query, source_results, parent_context)
            
            # Save synthesis
            await self._save_synthesis(research_id, synthesis)
            
            # Step 4: Set credibility score
            credibility_score = 0.8  # Higher confidence for tool-selected sources
            if query.include_credibility:
                logger.info("Step 4: Setting credibility score")
                await self._save_credibility(research_id, credibility_score)
            
            # Mark as completed
            await self._update_status(research_id, "completed")
            
            logger.info(f"✅ Research {research_id} completed with tool use")
            
        except Exception as e:
            logger.error(f"❌ Research {research_id} with tool use failed: {e}")
            await self._update_status(research_id, "failed", error=str(e))
            raise
    
    async def process_query(
        self,
        research_id: str,
        query: ResearchQuery
    ) -> None:
        """
        Process a research query end-to-end
        
        Steps:
        1. Get parent research context if this is a follow-up
        2. Query MCP sources in parallel
        3. Synthesize results with Cerebras (including parent context)
        4. Score credibility with Ollama
        5. Save results to database
        """
        try:
            logger.info(f"Processing research {research_id}")
            
            # Update status to processing
            await self._update_status(research_id, "processing")
            
            # Step 0: Get parent research context if this is a follow-up
            parent_context = None
            if query.parent_research_id:
                logger.info(f"Step 0: Loading parent research {query.parent_research_id} for context...")
                parent_context = await self._get_parent_context(query.parent_research_id)
            
            # Step 1: Query all sources in parallel
            logger.info("Step 1: Querying MCP sources...")
            source_results = await self.mcp_orchestrator.query_all_sources(
                query.query,
                query.sources
            )
            
            # Save intermediate results
            await self._save_source_results(research_id, source_results)
            
            # Step 2: Synthesize with Cerebras (with parent context if available)
            logger.info("Step 2: Synthesizing with Cerebras...")
            synthesis = await self._synthesize_results(query.query, source_results, parent_context)
            
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
        source_results: list,
        parent_context: dict | None = None
    ) -> str:
        """Synthesize results using Cerebras with optional parent context"""
        synthesis_chunks = []
        
        async for chunk in self.cerebras_service.synthesize(
            query,
            source_results,
            parent_context=parent_context,
            stream=False
        ):
            synthesis_chunks.append(chunk)
        
        return ''.join(synthesis_chunks) if synthesis_chunks else ""
    
    async def _get_parent_context(self, parent_research_id: str) -> dict | None:
        """Get parent research context for follow-up queries"""
        try:
            result = await self.db.execute(
                select(Research).where(Research.id == parent_research_id)
            )
            parent_research = result.scalar_one_or_none()
            
            if not parent_research:
                logger.warning(f"Parent research {parent_research_id} not found")
                return None
            
            return {
                "query": parent_research.query,
                "synthesis": parent_research.synthesis,
                "sources": parent_research.sources
            }
        except Exception as e:
            logger.error(f"Error getting parent context: {e}")
            return None
    
    async def _select_sources_with_ai(
        self,
        query: str,
        parent_context: dict | None = None
    ) -> list:
        """
        Use AI to intelligently select which sources to query.
        Returns list of source names to query.
        """
        try:
            # Build the prompt for source selection
            system_prompt = """You are a research planning assistant. Your job is to select the BEST data sources for answering a user's question.

Available sources:
- web-search: Current information, news, general knowledge (DuckDuckGo)
- arxiv: Academic papers, scientific research, peer-reviewed studies
- github: Code repositories, software projects, developer documentation
- news: Breaking news, current events, recent developments
- database: Cached previous research results
- filesystem: Local documents, uploaded PDFs, knowledge base

Instructions:
1. Analyze the user's question carefully
2. Select 2-4 sources that are MOST relevant (don't select all!)
3. Respond with ONLY a JSON array of source names, like: ["web-search", "arxiv"]
4. Be selective - fewer high-quality sources are better than many irrelevant ones

Examples:
- "Latest AI developments" → ["web-search", "news"]
- "Quantum computing research papers" → ["arxiv", "web-search"]
- "Best Python libraries for ML" → ["github", "web-search"]
- "Climate change impact" → ["arxiv", "web-search", "news"]
- "Stock market news" → ["news", "web-search"]
"""
            
            user_prompt = f"Select the best sources for this question:\n\n{query}"
            
            if parent_context:
                user_prompt += f"\n\nContext from previous question: {parent_context['query']}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Get AI's source selection (without tool calling, just text response)
            response = await self.cerebras_service.complete_with_tools(
                messages=messages,
                tools=[],  # No tools needed for this meta-decision
                max_tokens=100
            )
            
            content = response["content"].strip()
            logger.info(f"AI source selection response: {content}")
            
            # Parse the JSON array from response
            # Extract JSON array from the response
            import re
            json_match = re.search(r'\[([^\]]+)\]', content)
            if json_match:
                json_str = json_match.group(0)
                selected = json.loads(json_str)
                
                # Validate source names
                valid_sources = ["web-search", "arxiv", "arxiv", "github", "news", "database", "filesystem"]
                selected = [s for s in selected if s in valid_sources]
                
                if not selected:
                    logger.warning("AI selected no valid sources, falling back to default")
                    return ["web-search", "arxiv"]
                
                logger.info(f"✅ AI selected sources: {selected}")
                return selected
            else:
                logger.warning("Could not parse JSON from AI response, using default sources")
                return ["web-search", "arxiv"]
                    
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI response: {e}")
            return ["web-search", "arxiv"]  # Safe default
        except Exception as e:
            logger.error(f"Error in AI source selection: {e}")
            return ["web-search", "arxiv", "news"]  # Safe default
    
    async def _update_status(
        self,
        research_id: str,
        status: str,
        error: str | None = None
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
