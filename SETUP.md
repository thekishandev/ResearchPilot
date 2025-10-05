# Setup and Installation Guide

## Prerequisites

Ensure you have the following installed:
- **Docker** & **Docker Compose** (v2.0+)
- **Node.js** 18+ (for local frontend development)
- **Python** 3.11+ (for local backend development)
- **Ollama** (for local Llama inference)

## Quick Start (Docker Compose)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ResearchPilot.git
cd ResearchPilot
```

### 2. Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

Required variables:
```env
CEREBRAS_API_KEY=your_cerebras_api_key_here
NEWS_API_KEY=your_news_api_key_here  # Optional
GITHUB_TOKEN=your_github_token_here  # Optional
```

### 3. Pull Ollama Model

```bash
# Start Ollama service
docker-compose up -d ollama

# Wait for Ollama to start (30 seconds)
sleep 30

# Pull Llama 3.1 8B model
docker exec -it researchpilot-ollama ollama pull llama3.1:8b
```

### 4. Start All Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Local Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL (via Docker)
docker-compose up -d postgres redis

# Run backend
uvicorn app.main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### MCP Servers Development

Each MCP server can be developed independently:

```bash
cd mcp-servers/web-search

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --port 9001
```

## Troubleshooting

### Common Issues

**1. Ollama model not found**
```bash
# Pull the model manually
docker exec -it researchpilot-ollama ollama pull llama3.1:8b

# Verify
docker exec -it researchpilot-ollama ollama list
```

**2. Port conflicts**
```bash
# Check what's using the port
sudo lsof -i :8000

# Change ports in docker-compose.yml if needed
```

**3. MCP Gateway connection issues**
```bash
# Check gateway logs
docker logs researchpilot-mcp-gateway

# Restart gateway
docker-compose restart mcp-gateway
```

**4. Database connection errors**
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres

# Wait for PostgreSQL to initialize
sleep 10
```

### Performance Optimization

**For faster inference:**
1. Use GPU if available (uncomment GPU section in docker-compose.yml)
2. Increase PostgreSQL connection pool: `DB_POOL_SIZE=30`
3. Enable Redis caching: Ensure Redis is running

**For local development:**
```bash
# Use fewer MCP sources
# Edit gateway/config.json to disable unused sources

# Reduce Ollama context window
# Lower max_tokens in OllamaService
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Start all services
docker-compose up -d

# Run integration tests
python tests/integration/test_full_flow.py
```

## Deployment

### Production Backend (Render/Railway)

```bash
# Using Render
1. Connect GitHub repository
2. Add environment variables
3. Deploy from main branch

# Using Railway
railway login
railway init
railway up
```

### Production Frontend (Vercel/Netlify)

```bash
# Using Vercel
vercel --prod

# Using Netlify
netlify deploy --prod
```

## Monitoring

Access metrics at:
- **Prometheus metrics**: http://localhost:8000/metrics
- **MCP Gateway metrics**: http://localhost:9090

## Support

For issues:
1. Check logs: `docker-compose logs [service_name]`
2. Verify health: http://localhost:8000/health
3. Open GitHub issue with logs

## Next Steps

1. Read the [API Documentation](http://localhost:8000/docs)
2. Try example queries
3. Customize MCP sources in `gateway/config.json`
4. Add your own data sources
