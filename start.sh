#!/bin/bash

# Startup script for Trading Platform

set -e

echo "🚀 Starting Algorithmic Trading Platform..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi

# Use docker-compose or docker compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

# Create necessary directories
mkdir -p data logs

# Start services
echo "📦 Building and starting containers..."
$COMPOSE_CMD -f docker-compose.dev.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
$COMPOSE_CMD -f docker-compose.dev.yml ps

# Run database migrations
echo "🗄️  Running database migrations..."
$COMPOSE_CMD -f docker-compose.dev.yml exec backend alembic upgrade head || echo "⚠️  Migrations may have failed, but continuing..."

echo ""
echo "✅ Trading Platform is starting up!"
echo ""
echo "📍 Services available at:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo ""
echo "📊 View logs with: docker-compose -f docker-compose.dev.yml logs -f"
echo "🛑 Stop services with: docker-compose -f docker-compose.dev.yml down"
echo ""
