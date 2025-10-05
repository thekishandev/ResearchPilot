"""
MCP Orchestrator
Coordinates requests across multiple MCP servers (with gateway support)
"""
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime
import os

from app.core.config import settings
from app.core.monitoring import mcp_sources_active


class MCPOrchestrator:
    """Orchestrates requests to multiple MCP servers"""
    
    # Define available MCP sources with direct URLs
    SOURCES = {
        "web-search": {
            "url": os.getenv("MCP_WEB_SEARCH_URL", "http://mcp-web-search:9001"),
            "name": "Web Search"
        },
        "arxiv": {
            "url": os.getenv("MCP_ARXIV_URL", "http://mcp-arxiv:9002"),
            "name": "ArXiv Papers"
        },
        "database": {
            "url": os.getenv("MCP_DATABASE_URL", "http://mcp-database:9003"),
            "name": "Database Cache"
        },
        "filesystem": {
            "url": os.getenv("MCP_FILESYSTEM_URL", "http://mcp-filesystem:9004"),
            "name": "Filesystem Documents"
        },
        "github": {
            "url": os.getenv("MCP_GITHUB_URL", "http://mcp-github:9005"),
            "name": "GitHub Code Search"
        },
        "news": {
            "url": os.getenv("MCP_NEWS_URL", "http://mcp-news:9006"),
            "name": "News API"
        },
    }
    
    def __init__(self, use_gateway: bool = True):
        self.timeout = settings.MCP_GATEWAY_TIMEOUT
        self.max_concurrent = settings.MAX_CONCURRENT_SOURCES
        self.use_gateway = use_gateway and hasattr(settings, 'MCP_GATEWAY_URL') and settings.MCP_GATEWAY_URL
        self.gateway_url = getattr(settings, 'MCP_GATEWAY_URL', None)
        
        if self.use_gateway:
            logger.info(f"MCP Orchestrator using gateway: {self.gateway_url}")
        else:
            logger.info("MCP Orchestrator using direct source connections")
    
    async def query_all_sources(
        self,
        query: str,
        sources: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query multiple MCP sources in parallel
        
        Args:
            query: Search query
            sources: Specific sources to query (defaults to all)
        
        Returns:
            List of results from each source
        """
        # Determine which sources to query
        target_sources = sources if sources else list(self.SOURCES.keys())
        target_sources = [s for s in target_sources if s in self.SOURCES]
        
        logger.info(f"Querying {len(target_sources)} sources: {target_sources}")
        
        # Create tasks for parallel execution
        tasks = [
            self._query_source(source, query)
            for source in target_sources
        ]
        
        # Execute with concurrency limit
        results = []
        for i in range(0, len(tasks), self.max_concurrent):
            batch = tasks[i:i + self.max_concurrent]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
        
        # Filter out exceptions and update metrics
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Source query failed: {result}")
            else:
                valid_results.append(result)
        
        mcp_sources_active.set(len([r for r in valid_results if r.get('status') == 'success']))
        
        logger.info(f"Retrieved {len(valid_results)} valid results")
        return valid_results
    
    async def _query_source(
        self,
        source: str,
        query: str
    ) -> Dict[str, Any]:
        """
        Query a single MCP source (via gateway or direct)
        
        Args:
            source: Source identifier
            query: Search query
        
        Returns:
            Source result with status and data
        """
        start_time = asyncio.get_event_loop().time()
        source_info = self.SOURCES.get(source)
        
        if not source_info:
            return {
                "source": source,
                "status": "error",
                "error": "Unknown source",
                "response_time": 0,
            }
        
        try:
            # Choose routing method
            if self.use_gateway:
                # Route through MCP Gateway
                url = f"{self.gateway_url}/query/{source}"
                logger.debug(f"Querying {source} via gateway: {url}")
            else:
                # Direct connection to MCP server
                url = f"{source_info['url']}/search"
                logger.debug(f"Querying {source} directly: {url}")
            
            payload = {
                "query": query,
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response_time = asyncio.get_event_loop().time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Handle gateway response format
                        if self.use_gateway and "data" in data:
                            actual_data = data["data"]
                            gateway_time = data.get("response_time_ms", response_time * 1000)
                            logger.info(f"✓ {source} (gateway): Retrieved data in {gateway_time:.0f}ms")
                        else:
                            actual_data = data
                            logger.info(f"✓ {source} (direct): Retrieved data in {response_time:.2f}s")
                        
                        return {
                            "source": source,
                            "status": "success",
                            "data": actual_data,
                            "response_time": response_time,
                            "via_gateway": self.use_gateway,
                        }
                    else:
                        error_text = await response.text()
                        logger.warning(f"✗ {source}: Error {response.status}")
                        
                        return {
                            "source": source,
                            "status": "error",
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time,
                            "via_gateway": self.use_gateway,
                        }
                        
        except asyncio.TimeoutError:
            response_time = asyncio.get_event_loop().time() - start_time
            logger.warning(f"✗ {source}: Timeout after {response_time:.2f}s")
            
            return {
                "source": source,
                "status": "timeout",
                "error": "Request timeout",
                "response_time": response_time,
            }
            
        except Exception as e:
            response_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"✗ {source}: Exception - {e}")
            
            return {
                "source": source,
                "status": "error",
                "error": str(e),
                "response_time": response_time,
            }
    
    async def check_all_sources(self) -> List[Dict[str, Any]]:
        """Check health of all MCP sources"""
        tasks = [
            self.check_source(source)
            for source in self.SOURCES.keys()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Health check failed: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def check_source(self, source: str) -> Dict[str, Any]:
        """Check health of a specific source"""
        source_info = self.SOURCES.get(source)
        
        if not source_info:
            return {
                "name": source,
                "status": "unknown",
                "error": "Unknown source",
            }
        
        try:
            url = f"{source_info['url']}/health"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return {
                            "name": source,
                            "status": "healthy",
                            "last_check": datetime.utcnow(),
                        }
                    else:
                        return {
                            "name": source,
                            "status": "unhealthy",
                            "error": f"HTTP {response.status}",
                            "last_check": datetime.utcnow(),
                        }
                        
        except Exception as e:
            return {
                "name": source,
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow(),
            }
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        sources = await self.check_all_sources()
        
        total = len(sources)
        healthy = len([s for s in sources if s.get('status') == 'healthy'])
        unhealthy = total - healthy
        percentage = (healthy / total * 100) if total > 0 else 0
        
        return {
            "total": total,
            "healthy": healthy,
            "unhealthy": unhealthy,
            "percentage": percentage,
        }
