# 🚀 Quick Start Guide

## Run the Platform in 3 Steps

### Step 1: Start Docker Desktop
Make sure Docker Desktop is running on your machine.

### Step 2: Run the Startup Script

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

**Or manually:**
```bash
docker-compose -f docker-compose.dev.yml up --build -d
```

### Step 3: Access the Platform

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Common Commands

```bash
# Start services
docker-compose -f docker-compose.dev.yml up -d

# Stop services
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Restart a service
docker-compose -f docker-compose.dev.yml restart backend

# Check status
docker-compose -f docker-compose.dev.yml ps
```

## Troubleshooting

**Port already in use?**
- Change ports in `docker-compose.dev.yml`

**Containers won't start?**
```bash
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up --build -d
```

**Need to start fresh?**
```bash
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up --build -d
```

## What's Running?

- ✅ **Frontend** (React) - Port 3000
- ✅ **Backend** (FastAPI) - Port 8000
- ✅ **PostgreSQL** - Port 5432
- ✅ **Redis** - Port 6379

All services are connected and ready to use!

For detailed information, see [DOCKER_SETUP.md](./DOCKER_SETUP.md)
