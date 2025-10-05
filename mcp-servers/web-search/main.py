"""
MCP Server: Web Search
Provides web search functionality using DuckDuckGo
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from loguru import logger
from typing import List, Dict, Any
import asyncio

try:
    from duckduckgo_search import AsyncDDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    logger.warning("duckduckgo-search not available, using mock data")

app = FastAPI(title="MCP Web Search Server", version="1.0.0")


class SearchQuery(BaseModel):
    query: str
    max_results: int = 10


class SearchResult(BaseModel):
    results: List[Dict[str, Any]]
    count: int
    source: str = "web-search"


@app.get("/")
async def root():
    return {
        "name": "MCP Web Search Server",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "web-search",
        "ddgs_available": DDGS_AVAILABLE
    }


@app.post("/search", response_model=SearchResult)
async def search(query: SearchQuery):
    """
    Perform web search using DuckDuckGo
    """
    try:
        logger.info(f"Web search query: {query.query}")
        
        if DDGS_AVAILABLE:
            results = await perform_real_search(query.query, query.max_results)
        else:
            results = await perform_mock_search(query.query, query.max_results)
        
        return SearchResult(
            results=results,
            count=len(results),
            source="web-search"
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def perform_real_search(query: str, max_results: int) -> List[Dict[str, Any]]:
    """Perform real DuckDuckGo search"""
    try:
        async with AsyncDDGS() as ddgs:
            results = []
            async for result in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                })
            return results
    except Exception as e:
        logger.error(f"DuckDuckGo search failed: {e}")
        return await perform_mock_search(query, max_results)


async def perform_mock_search(query: str, max_results: int) -> List[Dict[str, Any]]:
    """Return mock search results"""
    await asyncio.sleep(0.5)  # Simulate API delay
    
    mock_results = [
        {
            "title": f"Mock result 1 for: {query}",
            "url": "https://example.com/result1",
            "snippet": f"This is a mock search result related to {query}. In production, this would be real DuckDuckGo data."
        },
        {
            "title": f"Mock result 2 for: {query}",
            "url": "https://example.com/result2",
            "snippet": f"Another mock result about {query} with relevant information."
        },
        {
            "title": f"Mock result 3 for: {query}",
            "url": "https://example.com/result3",
            "snippet": f"Third mock result providing context for {query}."
        }
    ]
    
    return mock_results[:max_results]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)
