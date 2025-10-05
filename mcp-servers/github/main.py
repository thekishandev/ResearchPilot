"""
MCP Server: GitHub
Searches GitHub repositories and code
"""
from fastapi import FastAPI
from pydantic import BaseModel
from loguru import logger
import aiohttp
import os

app = FastAPI(title="MCP GitHub Server", version="1.0.0")


class SearchQuery(BaseModel):
    query: str
    max_results: int = 10


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "github"}


@app.post("/search")
async def search(query: SearchQuery):
    try:
        logger.info(f"GitHub search: {query.query}")
        
        github_token = os.getenv("GITHUB_TOKEN", "")
        
        if github_token:
            # Real GitHub search (simplified)
            results = await search_github_api(query.query, github_token, query.max_results)
        else:
            # Mock results
            results = get_mock_results(query.query)
        
        return {"results": results, "count": len(results), "source": "github"}
        
    except Exception as e:
        logger.error(f"GitHub error: {e}")
        return {"results": get_mock_results(query.query), "count": 2, "source": "github"}


async def search_github_api(query: str, token: str, max_results: int):
    """Search GitHub API"""
    try:
        url = "https://api.github.com/search/repositories"
        headers = {"Authorization": f"token {token}"}
        params = {"q": query, "per_page": max_results}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        {
                            "name": item["name"],
                            "description": item.get("description", ""),
                            "url": item["html_url"],
                            "stars": item["stargazers_count"]
                        }
                        for item in data.get("items", [])[:max_results]
                    ]
    except Exception as e:
        logger.error(f"GitHub API error: {e}")
        return get_mock_results(query)


def get_mock_results(query: str):
    return [
        {
            "name": f"mock-repo-{query}",
            "description": f"A repository related to {query}",
            "url": "https://github.com/mock/repo",
            "stars": 100
        }
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9005)
