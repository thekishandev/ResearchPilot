"""
MCP Server: News
Fetches current news articles
"""
from fastapi import FastAPI
from pydantic import BaseModel
from loguru import logger
import aiohttp
import os

app = FastAPI(title="MCP News Server", version="1.0.0")


class SearchQuery(BaseModel):
    query: str
    max_results: int = 10


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "news"}


@app.post("/search")
async def search(query: SearchQuery):
    try:
        logger.info(f"News search: {query.query}")
        
        news_api_key = os.getenv("NEWS_API_KEY", "")
        
        if news_api_key:
            results = await search_news_api(query.query, news_api_key, query.max_results)
        else:
            results = get_mock_results(query.query)
        
        return {"results": results, "count": len(results), "source": "news"}
        
    except Exception as e:
        logger.error(f"News error: {e}")
        return {"results": get_mock_results(query.query), "count": 2, "source": "news"}


async def search_news_api(query: str, api_key: str, max_results: int):
    """Search News API"""
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": api_key,
            "pageSize": max_results,
            "sortBy": "relevancy"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        {
                            "title": article["title"],
                            "description": article.get("description", ""),
                            "url": article["url"],
                            "source": article["source"]["name"],
                            "publishedAt": article["publishedAt"]
                        }
                        for article in data.get("articles", [])[:max_results]
                    ]
    except Exception as e:
        logger.error(f"News API error: {e}")
        return get_mock_results(query)


def get_mock_results(query: str):
    return [
        {
            "title": f"Breaking News: {query}",
            "description": f"Latest developments regarding {query}...",
            "url": "https://news.example.com/article1",
            "source": "Mock News",
            "publishedAt": "2024-10-01T12:00:00Z"
        }
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9006)
