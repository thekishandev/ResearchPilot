# ResearchPilot 🚀

> Transform 2-8 hour manual research tasks into <10 second AI-synthesized intelligence reports

**FutureStack GenAI Hackathon Submission** (Sept 29 - Oct 5, 2024)

## Overview

ResearchPilot is an AI research copilot that orchestrates 10+ data sources using ultra-fast AI inference to deliver comprehensive research reports in seconds instead of hours.

### Target Users
- Analysts
- Researchers
- Journalists
- Consultants

## 🏆 Sponsor Technology Integration

### 1. Cerebras API (Primary)# PHASE 0 PROMPT — Project Initialization & Repository Setup

## Context
Refer to MASTER PROJECT CONTEXT. We're starting from scratch.

## Your Task
Set up the complete project structure with initial configurations, Docker setup, and development environment.

## Specific Requirements

### 1. Create Project Structure

Generate complete folder structure:
researchpilot/
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── .env.example
├── backend/
│   ├── app/
│   │   ├── init.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routers/
│   │   │   ├── init.py
│   │   │   └── research.py
│   │   ├── services/
│   │   │   ├── init.py
│   │   │   ├── cerebras_client.py
│   │   │   ├── mcp_orchestrator.py
│   │   │   └── llama_local.py
│   │   ├── models/
│   │   │   ├── init.py
│   │   │   └── schemas.py
│   │   └── db/
│   │       ├── init.py
│   │       └── database.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── mcp-servers/
│   ├── web-search/
│   │   ├── server.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── arxiv/
│   │   ├── server.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── database/
│   │   ├── server.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── filesystem/
│   │   ├── server.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── github/
│   │   ├── server.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── news/
│       ├── server.py
│       ├── requirements.txt
│       └── Dockerfile
├── gateway/
│   ├── config.json
│   └── interceptors/
│       ├── audit.py
│       ├── rate_limit.py
│       └── injection_guard.py
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
├── README.md
└── LICENSE


### 2. Generate Configuration Files

#### docker-compose.yml
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: researchpilot
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/researchpilot
      - CEREBRAS_API_KEY=${CEREBRAS_API_KEY}
      - OLLAMA_HOST=http://ollama:11434
      - MCP_GATEWAY_URL=http://mcp-gateway:3000
    depends_on:
      postgres:
        condition: service_healthy
      mcp-gateway:
        condition: service_started
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host

  # Docker MCP Gateway
  mcp-gateway:
    image: docker/mcp-gateway:latest
    ports:
      - "3000:3000"
    environment:
      - MCP_LOG_LEVEL=info
    volumes:
      - ./gateway/config.json:/config/gateway-config.json
      - ./gateway/interceptors:/interceptors
    depends_on:
      - mcp-web-search
      - mcp-arxiv
      - mcp-database
      - mcp-filesystem
      - mcp-github
      - mcp-news

  # MCP Servers
  mcp-web-search:
    build: ./mcp-servers/web-search
    environment:
      - SEARCH_PROVIDER=duckduckgo

  mcp-arxiv:
    build: ./mcp-servers/arxiv

  mcp-database:
    build: ./mcp-servers/database
    environment:
      - DB_URL=postgresql://postgres:postgres@postgres:5432/researchpilot
    depends_on:
      postgres:
        condition: service_healthy

  mcp-filesystem:
    build: ./mcp-servers/filesystem
    volumes:
      - ./research-docs:/docs

  mcp-github:
    build: ./mcp-servers/github
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}

  mcp-news:
    build: ./mcp-servers/news
    environment:
      - NEWS_API_KEY=${NEWS_API_KEY}

  # Ollama for local Llama inference
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  postgres_data:
  ollama_data:

- **Ultra-fast inference** using Llama 3.3 70B
- **Streaming responses** for real-time UX
- **Sub-2 second synthesis** of multi-source results
- Model: `llama-3.3-70b`

### 2. Meta Llama (Secondary)
- **Cloud:** Llama 3.3 70B via Cerebras for main synthesis
- **Edge:** Llama 3.1 8B via Ollama for credibility scoring
- Demonstrates both cloud and edge deployment

### 3. Docker MCP Gateway (Primary)
- Orchestrates **6+ MCP servers**
- Custom security interceptors (audit, rate-limit, injection prevention)
- Unified endpoint for all data sources

## 🏗️ Architecture

```
Frontend (React/TS)
    ↓ HTTP/SSE
Backend (FastAPI)
    ↓ Orchestrates
    ├→ Cerebras API (synthesis)
    └→ Docker MCP Gateway
        ↓ Routes to
        ├→ Web Search MCP Server
        ├→ ArXiv MCP Server
        ├→ Database MCP Server
        ├→ Filesystem MCP Server
        ├→ GitHub MCP Server
        └→ News MCP Server
```

## 🛠️ Technology Stack

### Frontend
- React 18 + TypeScript 5
- Vite build tool
- Tailwind CSS + shadcn/ui
- Server-Sent Events (SSE)
- React Query

### Backend
- Python 3.11+ with FastAPI
- Asyncio for parallel operations
- SQLAlchemy 2.0
- Pydantic v2
- SSE streaming

### Infrastructure
- PostgreSQL 15
- Docker Compose
- Ollama (local Llama)
- Docker MCP Gateway

## 📊 MCP Data Sources (6 Total)

1. **Web Search** - DuckDuckGo integration
2. **ArXiv Papers** - Academic research
3. **PostgreSQL Database** - Cached research + analytics
4. **Filesystem/Documents** - Local document search
5. **GitHub Code Search** - Code repository analysis
6. **News API** - Current news aggregation

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- Ollama (for local Llama inference)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/ResearchPilot.git
cd ResearchPilot
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Add your API keys
# - CEREBRAS_API_KEY
# - NEWS_API_KEY
# - GITHUB_TOKEN (optional)
```

### 3. Start Infrastructure
```bash
# Start all services
docker-compose up -d

# Verify services
docker-compose ps
```

### 4. Install Dependencies

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 5. Run Application

**Backend (Terminal 1):**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
researchpilot/
├── frontend/                 # React + TypeScript
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utilities
│   │   ├── types/           # TypeScript types
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── backend/                 # FastAPI
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core logic
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   └── main.py
│   └── requirements.txt
├── mcp-servers/            # MCP server implementations
│   ├── web-search/
│   ├── arxiv/
│   ├── database/
│   ├── filesystem/
│   ├── github/
│   └── news/
├── gateway/                # MCP Gateway config
│   └── config.json
├── docker-compose.yml      # Local orchestration
├── .env.example
└── README.md
```

## 🎯 Key Features

### 1. Ultra-Fast Research Synthesis
- Parallel data source querying
- Sub-2 second response time
- Real-time streaming results

### 2. Multi-Source Intelligence
- 6+ simultaneous data sources
- Automatic source credibility scoring
- Graceful degradation on source failures

### 3. Security & Reliability
- Custom MCP Gateway interceptors
- Rate limiting & audit logging
- SQL injection prevention
- No secrets in code (environment variables)

### 4. Rich User Experience
- Real-time streaming updates
- Source attribution
- Credibility scores
- Export to multiple formats

## 📈 Performance Metrics

- **Response Time:** <2 seconds for 5-source synthesis
- **Source Coverage:** 6+ simultaneous MCP servers
- **Uptime:** Graceful degradation with fallbacks
- **Code Quality:** TypeScript strict mode, Python type hints

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
```

## 📦 Deployment

### Backend (Render/Railway)
```bash
# Deploy to Render
render deploy

# Or Railway
railway up
```

### Frontend (Vercel/Netlify)
```bash
# Deploy to Vercel
vercel deploy --prod

# Or Netlify
netlify deploy --prod
```

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
CEREBRAS_API_KEY=your_cerebras_key
DATABASE_URL=postgresql://user:pass@localhost:5432/researchpilot
OLLAMA_HOST=http://localhost:11434
MCP_GATEWAY_URL=http://localhost:8080
NEWS_API_KEY=your_news_api_key
GITHUB_TOKEN=your_github_token
```

**Frontend (.env):**
```env
VITE_API_URL=http://localhost:8000
```

## 📖 API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

```
POST /api/v1/research/query
- Submit research query
- Returns: Streaming SSE response

GET /api/v1/research/{id}
- Retrieve completed research
- Returns: JSON report

GET /api/v1/sources/status
- Check MCP server health
- Returns: Source availability status
```

## 🤝 Contributing

This is a hackathon submission. For collaboration inquiries, please open an issue.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **Cerebras** for ultra-fast inference
- **Meta** for Llama models
- **Docker** for MCP Gateway
- **FutureStack** for hosting the hackathon

## 📧 Contact

For questions or demo requests, reach out via GitHub issues.

---

**Built for FutureStack GenAI Hackathon 2024** 🚀
