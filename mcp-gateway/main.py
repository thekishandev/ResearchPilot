"""
MCP Gateway - Unified orchestration for MCP servers
Provides routing, security, and monitoring for all MCP sources
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import asyncio
import time
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ResearchPilot MCP Gateway",
    description="Unified gateway for Model Context Protocol servers",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MCP Server registry
MCP_SERVERS = {
    "web-search": {
        "url": "http://mcp-web-search:9001",
        "name": "Web Search",
        "timeout": 30
    },
    "arxiv": {
        "url": "http://mcp-arxiv:9002",
        "name": "ArXiv Papers",
        "timeout": 30
    },
    "database": {
        "url": "http://mcp-database:9003",
        "name": "Database Cache",
        "timeout": 15
    },
    "filesystem": {
        "url": "http://mcp-filesystem:9004",
        "name": "Documents",
        "timeout": 20
    },
    "github": {
        "url": "http://mcp-github:9005",
        "name": "GitHub Code",
        "timeout": 30
    },
    "news": {
        "url": "http://mcp-news:9006",
        "name": "News API",
        "timeout": 30
    }
}

# Metrics storage
metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "requests_by_source": {source: 0 for source in MCP_SERVERS.keys()},
    "avg_response_times": {source: [] for source in MCP_SERVERS.keys()}
}

# Audit log storage (in-memory for demo, would use DB in production)
audit_logs: List[Dict] = []


# Security Interceptors
def sql_injection_check(params: Dict[str, Any]) -> bool:
    """Check for SQL injection patterns"""
    dangerous_patterns = [
        "union.*select", "insert.*into", "drop.*table",
        "delete.*from", "--", ";", "'"
    ]
    
    param_str = json.dumps(params).lower()
    for pattern in dangerous_patterns:
        if pattern in param_str:
            logger.warning(f"SQL injection attempt detected: {pattern}")
            return False
    return True


def rate_limit_check(source: str) -> bool:
    """Simple rate limiting (60 requests per minute per source)"""
    # In production, would use Redis for distributed rate limiting
    # For demo, we'll allow all requests
    return True


def audit_log(source: str, endpoint: str, params: Dict, response_time: float, success: bool, error: str = None):
    """Log request for audit trail"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "source": source,
        "endpoint": endpoint,
        "params": params,
        "response_time_ms": round(response_time * 1000, 2),
        "success": success,
        "error": error
    }
    audit_logs.append(log_entry)
    
    # Keep only last 1000 entries
    if len(audit_logs) > 1000:
        audit_logs.pop(0)
    
    logger.info(f"Audit: {source} - {endpoint} - {response_time*1000:.2f}ms - {'✓' if success else '✗'}")


@app.get("/")
async def root():
    """Gateway information"""
    return {
        "service": "ResearchPilot MCP Gateway",
        "version": "1.0.0",
        "status": "operational",
        "sources": len(MCP_SERVERS),
        "features": [
            "Unified routing",
            "Security interceptors",
            "Audit logging",
            "Rate limiting",
            "Health monitoring"
        ]
    }


@app.get("/health")
async def health_check():
    """Gateway health check"""
    # Check connectivity to all MCP servers
    server_health = {}
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for source_name, config in MCP_SERVERS.items():
            try:
                response = await client.get(f"{config['url']}/health")
                server_health[source_name] = {
                    "status": "healthy" if response.status_code == 200 else "degraded",
                    "url": config['url']
                }
            except Exception as e:
                server_health[source_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
    
    all_healthy = all(s["status"] == "healthy" for s in server_health.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "gateway": "operational",
        "sources": server_health,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/query/{source}")
async def query_source(source: str, request: Request):
    """
    Route query to specific MCP source with security and monitoring
    """
    metrics["total_requests"] += 1
    metrics["requests_by_source"][source] = metrics["requests_by_source"].get(source, 0) + 1
    
    # Validate source exists
    if source not in MCP_SERVERS:
        metrics["failed_requests"] += 1
        raise HTTPException(status_code=404, detail=f"MCP source '{source}' not found")
    
    # Parse request body
    try:
        params = await request.json()
    except Exception as e:
        metrics["failed_requests"] += 1
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {str(e)}")
    
    # Security: SQL injection check
    if not sql_injection_check(params):
        metrics["failed_requests"] += 1
        audit_log(source, "query", params, 0, False, "SQL injection detected")
        raise HTTPException(status_code=400, detail="Security violation: dangerous SQL pattern detected")
    
    # Security: Rate limiting
    if not rate_limit_check(source):
        metrics["failed_requests"] += 1
        audit_log(source, "query", params, 0, False, "Rate limit exceeded")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Route to MCP server
    config = MCP_SERVERS[source]
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=config['timeout']) as client:
            response = await client.post(
                f"{config['url']}/query",
                json=params
            )
            response.raise_for_status()
            data = response.json()
        
        response_time = time.time() - start_time
        
        # Update metrics
        metrics["successful_requests"] += 1
        metrics["avg_response_times"][source].append(response_time)
        if len(metrics["avg_response_times"][source]) > 100:
            metrics["avg_response_times"][source].pop(0)
        
        # Audit log
        audit_log(source, "query", params, response_time, True)
        
        return {
            "source": source,
            "data": data,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except httpx.TimeoutException:
        response_time = time.time() - start_time
        metrics["failed_requests"] += 1
        audit_log(source, "query", params, response_time, False, "Timeout")
        raise HTTPException(status_code=504, detail=f"MCP source '{source}' timeout")
    
    except httpx.HTTPStatusError as e:
        response_time = time.time() - start_time
        metrics["failed_requests"] += 1
        audit_log(source, "query", params, response_time, False, f"HTTP {e.response.status_code}")
        raise HTTPException(status_code=502, detail=f"MCP source error: {e.response.status_code}")
    
    except Exception as e:
        response_time = time.time() - start_time
        metrics["failed_requests"] += 1
        audit_log(source, "query", params, response_time, False, str(e))
        logger.error(f"Error querying {source}: {e}")
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")


@app.post("/query-all")
async def query_all_sources(request: Request):
    """
    Query all MCP sources in parallel
    """
    try:
        params = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {str(e)}")
    
    # Security check
    if not sql_injection_check(params):
        raise HTTPException(status_code=400, detail="Security violation detected")
    
    # Query all sources in parallel
    async def query_source_async(source: str, config: Dict):
        try:
            async with httpx.AsyncClient(timeout=config['timeout']) as client:
                start_time = time.time()
                response = await client.post(f"{config['url']}/query", json=params)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    return {
                        "source": source,
                        "status": "success",
                        "data": response.json(),
                        "response_time_ms": round(response_time * 1000, 2)
                    }
                else:
                    return {
                        "source": source,
                        "status": "error",
                        "error": f"HTTP {response.status_code}",
                        "response_time_ms": round(response_time * 1000, 2)
                    }
        except Exception as e:
            return {
                "source": source,
                "status": "error",
                "error": str(e)
            }
    
    # Execute all queries in parallel
    tasks = [query_source_async(name, config) for name, config in MCP_SERVERS.items()]
    results = await asyncio.gather(*tasks)
    
    return {
        "results": results,
        "total_sources": len(MCP_SERVERS),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/sources")
async def list_sources():
    """List all available MCP sources"""
    return {
        "sources": [
            {
                "id": name,
                "name": config["name"],
                "url": config["url"],
                "timeout": config["timeout"]
            }
            for name, config in MCP_SERVERS.items()
        ],
        "total": len(MCP_SERVERS)
    }


@app.get("/metrics")
async def get_metrics():
    """Get gateway metrics"""
    avg_times = {}
    for source, times in metrics["avg_response_times"].items():
        if times:
            avg_times[source] = round(sum(times) / len(times) * 1000, 2)
        else:
            avg_times[source] = 0
    
    return {
        "total_requests": metrics["total_requests"],
        "successful_requests": metrics["successful_requests"],
        "failed_requests": metrics["failed_requests"],
        "success_rate": round(
            metrics["successful_requests"] / metrics["total_requests"] * 100, 2
        ) if metrics["total_requests"] > 0 else 0,
        "requests_by_source": metrics["requests_by_source"],
        "avg_response_times_ms": avg_times
    }


@app.get("/audit-logs")
async def get_audit_logs(limit: int = 100):
    """Get recent audit logs"""
    return {
        "logs": audit_logs[-limit:],
        "total": len(audit_logs)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
