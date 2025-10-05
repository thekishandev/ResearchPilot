# 🚀 ResearchPilot - Getting Started Guide

## Welcome to ResearchPilot!

This guide will help you get ResearchPilot up and running in minutes.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Manual Setup](#manual-setup)
4. [Using the Application](#using-the-application)
5. [Troubleshooting](#troubleshooting)
6. [Next Steps](#next-steps)

---

## Prerequisites

Before you begin, ensure you have:

### Required Software
- **Docker** (v20.10+) & **Docker Compose** (v2.0+)
  ```bash
  # Check versions
  docker --version
  docker-compose --version
  ```

- **Cerebras API Key** (REQUIRED)
  - Sign up at: https://cerebras.ai/
  - Get your API key from the dashboard

### Optional
- **Node.js** 18+ (for local frontend development)
- **Python** 3.11+ (for local backend development)
- **News API Key**: https://newsapi.org/
- **GitHub Token**: https://github.com/settings/tokens

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space
- **OS**: Linux, macOS, or Windows with WSL2

---

## Quick Start

### Step 1: Configure Environment

```bash
cd /home/kishan/Downloads/Projects/Github/ResearchPilot

# Copy environment template
cp .env.example .env

# Edit .env and add your Cerebras API key
nano .env  # or use your preferred editor
```

In the `.env` file, set:
```env
CEREBRAS_API_KEY=your_actual_cerebras_key_here
```

### Step 2: Run the Start Script

```bash
# Make script executable (if not already)
chmod +x start.sh

# Run the start script
./start.sh
```

The script will:
1. ✅ Check Docker prerequisites
2. ✅ Start Ollama service
3. ✅ Pull Llama 3.1 8B model
4. ✅ Start all services
5. ✅ Perform health checks

### Step 3: Access the Application

Once the script completes:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Step 4: Try Your First Query

1. Open http://localhost:5173 in your browser
2. Enter a research query, for example:
   ```
   What are the latest breakthroughs in quantum computing?
   ```
3. Click "Start Research"
4. Watch real-time results stream in!

---

## Manual Setup

If you prefer manual setup or the script doesn't work:

### 1. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start Ollama and Pull Model
```bash
# Start Ollama
docker-compose up -d ollama

# Wait for Ollama to initialize (30 seconds)
sleep 30

# Pull Llama 3.1 8B model
docker exec -it researchpilot-ollama ollama pull llama3.1:8b

# Verify model is downloaded
docker exec -it researchpilot-ollama ollama list
```

### 3. Start All Services
```bash
# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Or view specific service logs
docker-compose logs -f backend
```

### 4. Verify Services
```bash
# Check service status
docker-compose ps

# All services should show "Up" or "healthy"
```

### 5. Test the API
```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return JSON with all components "healthy"
```

---

## Using the Application

### Web Interface

1. **Enter Query**: Type your research question (minimum 10 characters)

2. **Start Research**: Click the "Start Research" button

3. **Watch Progress**: See real-time updates as:
   - Sources are queried (Web, ArXiv, GitHub, News, etc.)
   - Results are collected
   - Cerebras synthesizes the report
   - Ollama scores credibility

4. **View Results**: 
   - Read the synthesized report
   - Check source attributions
   - See credibility score
   - Download as Markdown

### API Usage

#### Submit Research Query
```bash
curl -X POST http://localhost:8000/api/v1/research/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest breakthroughs in quantum computing?",
    "include_credibility": true
  }'
```

#### Get Research Status
```bash
curl http://localhost:8000/api/v1/research/{research_id}
```

#### Check Source Health
```bash
curl http://localhost:8000/api/v1/sources/status
```

### Example Queries

Try these example queries:

1. **Technology**:
   - "Latest developments in artificial intelligence"
   - "Current state of quantum computing research"
   - "Breakthrough in renewable energy technology"

2. **Science**:
   - "Recent discoveries in astrophysics"
   - "Advances in CRISPR gene editing"
   - "Climate change mitigation strategies"

3. **Business**:
   - "Impact of AI on software development"
   - "Trends in electric vehicle market"
   - "Future of remote work technology"

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
```bash
# Find what's using the port
sudo lsof -i :8000

# Either stop that process or change the port in docker-compose.yml
```

#### 2. Ollama Model Not Found

**Error**: Research fails with "model not found"

**Solution**:
```bash
# Pull the model manually
docker exec -it researchpilot-ollama ollama pull llama3.1:8b

# Verify
docker exec -it researchpilot-ollama ollama list
```

#### 3. Cerebras API Errors

**Error**: "Cerebras API error: 401 Unauthorized"

**Solution**:
```bash
# Check your API key in .env
cat .env | grep CEREBRAS

# Make sure it's set correctly
# Restart services after updating
docker-compose restart backend
```

#### 4. Database Connection Errors

**Error**: "could not connect to database"

**Solution**:
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres

# Wait for PostgreSQL to initialize
sleep 10

# Check logs
docker-compose logs postgres
```

#### 5. Frontend Not Loading

**Error**: Blank page or "Cannot connect"

**Solution**:
```bash
# Check frontend logs
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend

# Access directly: http://localhost:5173
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f mcp-gateway
docker-compose logs -f ollama

# Last 100 lines
docker-compose logs --tail=100
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend

# Full reset (removes volumes)
docker-compose down -v
docker-compose up -d
```

### Check Service Health

```bash
# Backend health
curl http://localhost:8000/health

# Frontend (should return HTML)
curl http://localhost:5173

# MCP Gateway
curl http://localhost:8080/health

# Ollama
curl http://localhost:11434/api/tags
```

---

## Next Steps

### Customize the Application

1. **Add More MCP Sources**
   - Create new server in `mcp-servers/`
   - Add to `gateway/config.json`
   - Rebuild: `docker-compose up -d --build`

2. **Modify Synthesis Prompts**
   - Edit `backend/app/services/cerebras_service.py`
   - Adjust `_build_synthesis_prompt()` method

3. **Customize UI**
   - Edit components in `frontend/src/components/`
   - Modify styles in `frontend/src/index.css`
   - Rebuild: `docker-compose restart frontend`

### Local Development

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start with hot reload
uvicorn app.main:app --reload --port 8000
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Deploy to Production

#### Backend (Render/Railway)
1. Push to GitHub
2. Connect repository
3. Add environment variables
4. Deploy

#### Frontend (Vercel/Netlify)
```bash
cd frontend
vercel --prod
# or
netlify deploy --prod
```

### Read the Documentation

- **README.md**: Project overview
- **API.md**: Complete API reference
- **SETUP.md**: Detailed setup guide
- **PROJECT_SUMMARY.md**: Implementation details

### Explore the API

Visit http://localhost:8000/docs for interactive API documentation with:
- Try out endpoints
- See request/response schemas
- Test streaming responses

---

## Support & Resources

### Documentation
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

### Getting Help

1. **Check Logs**: Always start with `docker-compose logs -f`
2. **Health Check**: Visit http://localhost:8000/health
3. **GitHub Issues**: Open an issue with logs and error messages

### Performance Tips

- **Use GPU**: Uncomment GPU section in `docker-compose.yml` for Ollama
- **Increase Cache**: Adjust `CACHE_TTL` in `.env`
- **More Workers**: Increase `DB_POOL_SIZE` for higher load

---

## 🎉 You're All Set!

ResearchPilot is now running. Start researching and enjoy ultra-fast AI-powered intelligence synthesis!

**Happy Researching! 🚀**

---

## Quick Reference

```bash
# Start everything
./start.sh

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Full reset
docker-compose down -v
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Access frontend
http://localhost:5173

# Access API docs
http://localhost:8000/docs
```
