"""
Monitoring and metrics setup
"""
from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from time import time
from loguru import logger

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

research_queries_total = Counter(
    'research_queries_total',
    'Total research queries processed'
)

research_query_duration_seconds = Histogram(
    'research_query_duration_seconds',
    'Research query processing duration'
)

mcp_sources_active = Gauge(
    'mcp_sources_active',
    'Number of active MCP sources'
)

cerebras_api_calls_total = Counter(
    'cerebras_api_calls_total',
    'Total Cerebras API calls',
    ['model', 'status']
)

ollama_api_calls_total = Counter(
    'ollama_api_calls_total',
    'Total Ollama API calls',
    ['model', 'status']
)


def setup_monitoring(app: FastAPI):
    """Setup monitoring and metrics"""
    
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        """Collect HTTP metrics"""
        start_time = time()
        
        try:
            response = await call_next(request)
            duration = time() - start_time
            
            # Record metrics
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            return response
        except Exception as e:
            duration = time() - start_time
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=500
            ).inc()
            
            logger.error(f"Request failed: {e}")
            raise
    
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint"""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
    logger.info("✅ Monitoring setup complete")
