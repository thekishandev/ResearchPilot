"""
MCP Server: Filesystem
Searches local documents and files
"""
from fastapi import FastAPI
from pydantic import BaseModel
from loguru import logger

app = FastAPI(title="MCP Filesystem Server", version="1.0.0")


class SearchQuery(BaseModel):
    query: str
    max_results: int = 10


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "filesystem"}


@app.post("/search")
async def search(query: SearchQuery):
    try:
        logger.info(f"Filesystem search: {query.query}")
        
        # Mock document results
        results = [
            {
                "filename": f"document_about_{query.query}.pdf",
                "path": "/documents/research/",
                "content_snippet": f"This document discusses {query.query}...",
                "size": "1.2 MB"
            }
        ]
        
        return {"results": results, "count": len(results), "source": "filesystem"}
        
    except Exception as e:
        logger.error(f"Filesystem error: {e}")
        return {"results": [], "count": 0, "source": "filesystem"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9004)
