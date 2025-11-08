#!/bin/bash

# Entrypoint script for backend container

set -e

echo "🚀 Starting Trading Platform Backend..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if python -c "from sqlalchemy import create_engine, text; engine = create_engine('${DATABASE_URL}'); conn = engine.connect(); conn.execute(text('SELECT 1')); conn.close()" 2>/dev/null; then
    echo "✅ Database is ready!"
    break
  fi
  RETRY_COUNT=$((RETRY_COUNT + 1))
  echo "Database is unavailable - sleeping (attempt $RETRY_COUNT/$MAX_RETRIES)"
  sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  echo "❌ Database connection failed after $MAX_RETRIES attempts"
  exit 1
fi

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head || {
  echo "⚠️  Migration failed, but continuing..."
}

# Start the application
echo "🎯 Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
