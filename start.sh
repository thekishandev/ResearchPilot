#!/bin/bash

# ResearchPilot Quick Start Script
# This script sets up and runs the entire ResearchPilot application

set -e

echo "🚀 ResearchPilot Quick Start"
echo "=============================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your CEREBRAS_API_KEY before continuing."
    echo "   Then run this script again."
    exit 0
fi

# Check if CEREBRAS_API_KEY is set
if ! grep -q "CEREBRAS_API_KEY=your" .env && grep -q "CEREBRAS_API_KEY=" .env; then
    echo "✅ Environment variables configured"
else
    echo "⚠️  CEREBRAS_API_KEY not set in .env file"
    echo "   Please add your Cerebras API key before continuing."
    exit 1
fi

echo ""
echo "🔧 Starting services..."
echo ""

# Start Ollama first
echo "Starting Ollama service..."
docker compose up -d ollama

echo "Waiting for Ollama to be ready (30 seconds)..."
sleep 30

# Pull Llama model
echo "Pulling Llama 3.1 8B model..."
docker exec -it researchpilot-ollama ollama pull llama3.1:8b || echo "Model already exists or pull failed (continuing anyway)"

# Start all other services
echo ""
echo "Starting all services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to initialize (60 seconds)..."
sleep 60

# Check health
echo ""
echo "🏥 Checking service health..."

if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API is healthy"
else
    echo "⚠️  Backend API not responding yet (may need more time)"
fi

if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ Frontend is accessible"
else
    echo "⚠️  Frontend not responding yet (may need more time)"
fi

echo ""
echo "=============================="
echo "🎉 ResearchPilot is running!"
echo "=============================="
echo ""
echo "Access the application at:"
echo "  🌐 Frontend:        http://localhost:5173"
echo "  🔧 Backend API:     http://localhost:8000"
echo "  📖 API Docs:        http://localhost:8000/docs"
echo "  ❤️  Health Check:   http://localhost:8000/health"
echo ""
echo "View logs with:"
echo "  docker compose logs -f"
echo ""
echo "Stop services with:"
echo "  docker compose down"
echo ""
echo "Happy researching! 🚀"
