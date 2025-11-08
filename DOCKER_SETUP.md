# Docker Setup Guide

This guide will help you run the Algorithmic Trading Platform using Docker containers.

## Prerequisites

- **Docker Desktop** installed and running
  - [Download for Windows/Mac](https://www.docker.com/products/docker-desktop)
  - [Install for Linux](https://docs.docker.com/engine/install/)
- **Docker Compose** (included with Docker Desktop)
- At least **4GB RAM** available for Docker
- At least **10GB** free disk space

## Quick Start

### Option 1: Using Startup Scripts (Recommended)

#### On Linux/Mac:
```bash
# Make scripts executable
chmod +x start.sh stop.sh

# Start the platform
./start.sh
```

#### On Windows:
```cmd
# Double-click start.bat or run in Command Prompt
start.bat
```

### Option 2: Using Docker Compose Directly

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up --build -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop all services
docker-compose -f docker-compose.dev.yml down
```

## Services

The platform includes the following services:

| Service | Port | Description |
|---------|------|-------------|
| **Frontend** | 3000 | React application |
| **Backend API** | 8000 | FastAPI backend |
| **PostgreSQL** | 5432 | Main database |
| **Redis** | 6379 | Cache and task queue |

## Accessing the Platform

Once the containers are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Common Commands

### Start Services
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### Stop Services
```bash
docker-compose -f docker-compose.dev.yml down
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend
```

### Restart a Service
```bash
docker-compose -f docker-compose.dev.yml restart backend
```

### Rebuild Containers
```bash
docker-compose -f docker-compose.dev.yml up --build -d
```

### Run Database Migrations
```bash
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head
```

### Access Container Shell
```bash
# Backend container
docker-compose -f docker-compose.dev.yml exec backend bash

# Frontend container
docker-compose -f docker-compose.dev.yml exec frontend sh
```

### View Running Containers
```bash
docker-compose -f docker-compose.dev.yml ps
```

## Troubleshooting

### Port Already in Use

If you get an error about ports being in use:

```bash
# Check what's using the port
# Linux/Mac
lsof -i :3000
lsof -i :8000

# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Change ports in docker-compose.dev.yml if needed
```

### Containers Won't Start

1. **Check Docker is running**:
   ```bash
   docker info
   ```

2. **Check logs for errors**:
   ```bash
   docker-compose -f docker-compose.dev.yml logs
   ```

3. **Rebuild containers**:
   ```bash
   docker-compose -f docker-compose.dev.yml down
   docker-compose -f docker-compose.dev.yml up --build -d
   ```

### Database Connection Issues

1. **Wait for database to be ready**:
   ```bash
   docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U postgres
   ```

2. **Check database logs**:
   ```bash
   docker-compose -f docker-compose.dev.yml logs postgres
   ```

### Frontend Not Loading

1. **Check if frontend container is running**:
   ```bash
   docker-compose -f docker-compose.dev.yml ps frontend
   ```

2. **Check frontend logs**:
   ```bash
   docker-compose -f docker-compose.dev.yml logs frontend
   ```

3. **Rebuild frontend**:
   ```bash
   docker-compose -f docker-compose.dev.yml up --build frontend
   ```

### Clear Everything and Start Fresh

```bash
# Stop and remove all containers, networks, and volumes
docker-compose -f docker-compose.dev.yml down -v

# Remove all images
docker-compose -f docker-compose.dev.yml down --rmi all

# Start fresh
docker-compose -f docker-compose.dev.yml up --build -d
```

## Development Mode

The `docker-compose.dev.yml` file is configured for development with:

- **Hot reload** enabled for both frontend and backend
- **Volume mounting** for live code changes
- **Debug mode** enabled
- **Development dependencies** included

## Production Mode

For production deployment, use the full `docker-compose.yml` which includes:

- Production builds
- Nginx reverse proxy
- Monitoring (Prometheus, Grafana)
- TimescaleDB for time-series data
- Celery workers for background tasks

## Environment Variables

You can customize the configuration by creating a `.env` file:

```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/trading_platform
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## Data Persistence

Data is persisted in Docker volumes:

- `postgres_data`: Database data
- `redis_data`: Redis data
- `backend_logs`: Application logs

To backup data:
```bash
docker-compose -f docker-compose.dev.yml exec postgres pg_dump -U postgres trading_platform > backup.sql
```

## Resource Usage

Typical resource usage:

- **Memory**: ~2-3GB total
- **CPU**: Low to moderate
- **Disk**: ~5GB for images and volumes

## Next Steps

1. Access the frontend at http://localhost:3000
2. Check the API documentation at http://localhost:8000/docs
3. Create your first strategy
4. Run a backtest
5. Explore the analytics dashboard

## Support

If you encounter issues:

1. Check the logs: `docker-compose -f docker-compose.dev.yml logs`
2. Verify Docker is running: `docker info`
3. Check system resources: `docker stats`
4. Review the troubleshooting section above
