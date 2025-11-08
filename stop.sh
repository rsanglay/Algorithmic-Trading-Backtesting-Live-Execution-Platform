#!/bin/bash

# Stop script for Trading Platform

set -e

echo "🛑 Stopping Algorithmic Trading Platform..."

# Use docker-compose or docker compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

# Stop services
$COMPOSE_CMD -f docker-compose.dev.yml down

echo "✅ Trading Platform stopped!"
