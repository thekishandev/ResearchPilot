# API Documentation

## Base URL
- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://your-domain.com/api/v1`

## Authentication
Currently, the API does not require authentication. Future versions will implement API key authentication.

## Endpoints

### Research Endpoints

#### Submit Research Query
Submit a new research query for processing.

**Endpoint**: `POST /research/query`

**Request Body**:
```json
{
  "query": "What are the latest breakthroughs in quantum computing?",
  "sources": ["web-search", "arxiv", "news"],  // Optional
  "max_sources": 6,  // Optional, default: 6
  "include_credibility": true  // Optional, default: true
}
```

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Research query submitted successfully"
}
```

---

#### Stream Research Results
Get real-time streaming results via Server-Sent Events (SSE).

**Endpoint**: `GET /research/stream/{research_id}`

**Response**: `text/event-stream`
```
data: {"status": "processing", "sources": [...], "results": [...]}

data: {"status": "completed", "synthesis": "...", "credibility_score": 0.85}
```

---

#### Get Research Status
Retrieve the current status and results of a research query.

**Endpoint**: `GET /research/{research_id}`

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "query": "What are the latest breakthroughs in quantum computing?",
  "sources": ["web-search", "arxiv", "news"],
  "results": [
    {
      "source": "web-search",
      "status": "success",
      "data": {...},
      "response_time": 1.23
    }
  ],
  "synthesis": "# Quantum Computing Breakthroughs\n\n...",
  "credibility_score": 0.85,
  "created_at": "2024-10-01T12:00:00Z",
  "completed_at": "2024-10-01T12:00:08Z"
}
```

---

#### Delete Research
Delete a research query and its results.

**Endpoint**: `DELETE /research/{research_id}`

**Response**: `200 OK`
```json
{
  "message": "Research deleted successfully"
}
```

---

### Source Endpoints

#### Get All Sources Status
Check the health status of all MCP sources.

**Endpoint**: `GET /sources/status`

**Response**: `200 OK`
```json
[
  {
    "name": "web-search",
    "status": "healthy",
    "response_time": 0.45,
    "last_check": "2024-10-01T12:00:00Z"
  },
  {
    "name": "arxiv",
    "status": "healthy",
    "response_time": 1.23,
    "last_check": "2024-10-01T12:00:00Z"
  }
]
```

---

#### Get Source Health Summary
Get overall health summary of all sources.

**Endpoint**: `GET /sources/health`

**Response**: `200 OK`
```json
{
  "total_sources": 6,
  "healthy_sources": 5,
  "unhealthy_sources": 1,
  "health_percentage": 83.33
}
```

---

#### Get Specific Source Status
Check the status of a specific MCP source.

**Endpoint**: `GET /sources/{source_name}/status`

**Response**: `200 OK`
```json
{
  "name": "web-search",
  "status": "healthy",
  "response_time": 0.45,
  "last_check": "2024-10-01T12:00:00Z"
}
```

---

### Health Endpoints

#### System Health Check
Comprehensive health check for all system components.

**Endpoint**: `GET /health`

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "mcp_gateway": {
      "status": "healthy",
      "message": "MCP Gateway operational"
    },
    "ollama": {
      "status": "healthy",
      "message": "Ollama operational"
    },
    "cerebras": {
      "status": "healthy",
      "message": "Cerebras API key configured"
    }
  }
}
```

---

### Metrics Endpoint

#### Prometheus Metrics
Get Prometheus-compatible metrics.

**Endpoint**: `GET /metrics`

**Response**: `text/plain`
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/api/v1/research/query",status="200"} 42

# HELP research_queries_total Total research queries processed
# TYPE research_queries_total counter
research_queries_total 42

# HELP cerebras_api_calls_total Total Cerebras API calls
# TYPE cerebras_api_calls_total counter
cerebras_api_calls_total{model="llama-3.3-70b",status="success"} 38
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Query too short (minimum 10 characters)"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Research not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

- **Limit**: 60 requests per minute per IP
- **Burst**: 10 requests

When rate limit is exceeded:
```json
{
  "error": "Rate Limit Exceeded",
  "message": "Too many requests. Please try again later."
}
```

---

## Examples

### Python Example
```python
import requests

# Submit research query
response = requests.post(
    "http://localhost:8000/api/v1/research/query",
    json={
        "query": "What are the latest breakthroughs in quantum computing?",
        "include_credibility": True
    }
)
research_id = response.json()["id"]

# Get results
results = requests.get(
    f"http://localhost:8000/api/v1/research/{research_id}"
)
print(results.json()["synthesis"])
```

### JavaScript Example
```javascript
// Submit research query
const response = await fetch('http://localhost:8000/api/v1/research/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'What are the latest breakthroughs in quantum computing?',
    include_credibility: true
  })
});

const { id } = await response.json();

// Stream results
const eventSource = new EventSource(
  `http://localhost:8000/api/v1/research/stream/${id}`
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Status:', data.status);
  
  if (data.status === 'completed') {
    console.log('Synthesis:', data.synthesis);
    eventSource.close();
  }
};
```

### cURL Example
```bash
# Submit query
curl -X POST http://localhost:8000/api/v1/research/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest breakthroughs in quantum computing?",
    "include_credibility": true
  }'

# Get results
curl http://localhost:8000/api/v1/research/{research_id}

# Check health
curl http://localhost:8000/health
```

---

## WebSocket Support
Future versions will support WebSocket connections for real-time bidirectional communication.

---

For more information, visit the interactive documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
